
# Clean querydict
def clean_querydict(querydict):
    return {k: v[-1] for k, v in querydict.lists()}