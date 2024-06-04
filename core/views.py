from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import *
from organisers.models import *
from api.serializer import *
from django.db import IntegrityError
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from organisers.forms import *
from .utils import *
from sportshunt.conf import dev as settings
import razorpay
from django.views.decorators.csrf import csrf_exempt


def index(req):
    messages = req._messages
    now = timezone.now()
    now_date = now.date()
    end_date = now + timedelta(days=15)
    upcoming_tournaments = Tournament.objects.filter(start_date__range=(now, end_date)).order_by('start_date')[:4]    
    ongoing_tournaments = Tournament.objects.filter(start_date=now_date)[:4]
    recent_tournaments = Tournament.objects.filter(start_date__lt=now_date).order_by('-start_date')[:4]
    
    return render(req, "core/index.html", {
        "messages":messages,
        "upcoming_tournaments": upcoming_tournaments,
        "ongoing_tournaments": ongoing_tournaments,
        "recent_tournaments": recent_tournaments,
    })

def login_view(req):
    if req.method == "POST":
        username = req.POST["username"]
        password = req.POST["password"]
        user = authenticate(req, username=username, password=password)

        if user is not None:
            login(req, user)
            if user.is_organiser:
                return HttpResponseRedirect(reverse("organisers:index"))
            return HttpResponseRedirect(reverse("core:index"))
        else:
            messages.add_message(req, messages.ERROR, 'Invalid Username/ Password')
            return render(req, "auth/login.html")
    return render(req, "auth/login.html", {})

def logout_view(req):
    logout(req)
    return HttpResponseRedirect(reverse("core:index"))

def register_view(req):
    if req.method == "POST":
        user = validateRegister(req)
        if user:
            login(req, user)
            return redirect("core:verifyMail")
        
        return render(req, "auth/register.html")
    else:
        return render(req, "auth/register.html")

@login_required(login_url="/login/")
def verifyMail_view(req):
    user = req.user
    user_instance = User.objects.get(id=user.id)
    
    if user.verified:
        messages.add_message(req, messages.INFO, 'Email already verified')
        return redirect("core:index")
    
    if req.method == "POST":
        otp = req.POST["otp"]
        valid_otp = user_instance.otp == otp and user_instance.otpTime > timezone.now() - timezone.timedelta(minutes=5)
        if valid_otp:
            user_instance.verified = True
            user_instance.save()
            messages.add_message(req, messages.SUCCESS, 'Email Verified Successfully')
            
            if user.is_organiser:
                return HttpResponseRedirect(reverse("organisers:index"))
            return HttpResponseRedirect(reverse("core:index"))
        
        messages.add_message(req, messages.ERROR, 'Invalid OTP or OTP Expired')
        return render(req, "auth/verifyMail.html") 
    
    print(user_instance.otpTime)
    if not user_instance.otpTime or user_instance.otpTime < timezone.now() - timezone.timedelta(minutes=5):
        if sendOTP(user_instance):
            messages.add_message(req, messages.INFO, 'OTP sent to your email')
        else:
            messages.add_message(req, messages.ERROR, 'Error sending OTP')            

    return render(req, "auth/verifyMail.html")


def organisation_view(req, org_name):
    if not (Organisation.objects.filter(name=org_name).exists()):
        return render(req, "errors/organisation_not_found.html", {
            "org_name": org_name,
        })
    org_data = Organisation.objects.get(name=org_name)
    serializer = orgSerlializer(org_data, many=False)
    return render(req, "core/organisation.html", {
        "org_data": serializer.data,
    })

def tournament_view(req, tournament_name):
    if not (Tournament.objects.filter(name=tournament_name).exists()):
        return render(req, "errors/tournament_not_found.html", {
            "tournament_name": tournament_name, 
        })
    tournament = Tournament.objects.get(name=tournament_name)
    serializer = OrgTournamentSerializer(tournament, many=False)
    print(serializer.data)
    return render(req, "core/tournament.html", {
        "tournament_data": serializer.data,  
    })
    
# have to create a category view
def category_view(req, tournament_name, category_name):
    tournament_instance = Tournament.objects.get(name=tournament_name)
    category_instance = Category.objects.get(catagory_type=category_name, tournament=tournament_instance)    
    data = CategoryViewSerializer(category_instance, many=False).data
    fixture_data = data['fixture']
    teams = [team['members'] for team in data["teams"]]
    
    upcoming_matches, stage = None, "Not Started"
    if fixture_data:
        upcoming_matches = fixture_data["currentBracket"]
        stages_dict = {
            None: 'Not Started',
            0: 'Completed',
            1: 'Finals',
            2: 'Semi Finals',
            3: 'Quater Finals',
            4: 'Round of 16',
            5: 'Round of 32',
        }
        stage = stages_dict.get(int(fixture_data["currentStage"]), None)
    
    return render(req, "core/category.html", {
        "category_data": data,
        "tournament_data": tournament_instance,
        "fixture_id": fixture_data['id'] if fixture_data else None,
        "teams": teams,
        "upcoming_matches": upcoming_matches,
        "stage": stage,
    })

@login_required(login_url="/login/") # maybe rewrite this
def cart_view(req):
    user = User.objects.get(username=req.user)
    cart = user.cart.all()
    cart_data = []
    total = 0
    for item in cart:
        item_dict = {}
        item_dict["members"] = [f'{player.name}' for player in item.members.all()]
        item_dict["category"] = item.category
        if not item.category.registered:
            cart_data.append(item_dict)
            total += item.category.price
        else:
            user.cart.remove(item)
            user.save()
    return render(req, "core/cart.html", {
        "cart": cart_data,
        "total":total,
    })

@csrf_exempt
def checkout(req):
    if req.method != "POST":
        return render(req, "errors/404.html")
    
    payment_id = req.POST.get('razorpay_payment_id', '')
    razorpay_order_id = req.POST.get('razorpay_order_id', '')
    signature = req.POST.get('razorpay_signature', '')
    
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    if order_instance := Order.objects.filter(order_id=razorpay_order_id).exists():
        order_instance = Order.objects.get(order_id=razorpay_order_id)
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,
                                settings.RAZOR_KEY_SECRET))
        
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if result is not None:
            amount = order_instance.amount
            try:
                razorpay_client.payment.capture(payment_id, amount)
                order_instance.status = 'paid'
                order_instance.save()
                #checkout
                user_instance = order_instance.user
                cart_data = user_instance.cart.all()
                for item in cart_data:
                    item.category.teams.add(item)
                user_instance.cart.remove(*cart_data)
                user_instance.cart.clear()
                
                messages.add_message(req, messages.SUCCESS, 'Payment successful, and checkout done.')
                return redirect('core:cart')
            
            except Exception as e:
                messages.add_message(req, messages.ERROR, f'Payment failed {e}')
                return redirect('core:cart')
    else:
        return render(req, "payments/failed.html")
    
    order_instance.status = 'failed'
    order_instance.save()
    return render(req, "payments/failed.html")