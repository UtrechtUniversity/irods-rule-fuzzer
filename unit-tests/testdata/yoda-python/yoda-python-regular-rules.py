@rule.make(inputs=[0], outputs=[1])
def rule_group_expiration_date_validate(ctx, expiration_date):
    """Validation of expiration date.

    :param ctx:             Combined type of a callback and rei struct
    :param expiration_date: String containing date that has to be validated

    :returns: Indication whether expiration date is an accepted value
    """
    if expiration_date in ["", "."]:
        return 'true'

    try:
        if expiration_date != datetime.strptime(expiration_date, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError

        # Expiration date should be in the future
        if expiration_date <= datetime.now().strftime('%Y-%m-%d'):
            raise ValueError
        return 'true'
    except ValueError:
        return 'false'
