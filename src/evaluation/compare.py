def compare_evaluations(eval_v1: dict, eval_v2: dict) -> dict:
    """
    Compares two evaluation results side by side.
    """
    comparison = {}
    for key in eval_v1.keys():
        if key in eval_v2:
            comparison[key] = {
                "v1": eval_v1[key],
                "v2": eval_v2[key]
            }
    return comparison
