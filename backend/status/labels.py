FINAL = 'final/operative'
FUTURE = 'future-effective'
SUPERSEDED = 'superseded/historical'
PROPOSED = 'proposed/consultation'
EXPLANATORY = 'explanatory/supporting'

FIVE_STATUSES = (FINAL, FUTURE, SUPERSEDED, PROPOSED, EXPLANATORY)


def is_valid_status(label):
    return label in FIVE_STATUSES
