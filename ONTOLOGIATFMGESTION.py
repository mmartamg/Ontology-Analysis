from owlready2 import *
import math

CIS_POSTURE_SCORE = {
    "assumed": 100,
    "mitigated": 5,
    "delegated": 75
}

def create_query(func):
    def wrapper(*args, **kwargs):
        if "where" in kwargs:
            where = kwargs.pop("where")
        else:
            where = args.pop(-1)
        
        return f"""
            PREFIX onto: <ONTOLOGY PREFIX>
            { func(*args, **kwargs) }
            WHERE {{ { where } }}
        """
    return wrapper

@create_query
def create_select(select):
    return f"SELECT { select }"

@create_query
def create_insert(insert):
    return f"""
        INSERT {{ { insert } }}
    """

@create_query
def create_delete(delete):
    return f"""
        DELETE {{ { delete } }}
    """

@create_query
def create_replace(insert, delete):
    return f"""
        DELETE {{ { delete } }}
        INSERT {{ { insert } }}
    """

def get_individual_name(individual):
    return str(individual).split(".")[1]

def get_median(values):
    if len(values) == 0:
        return 0
    return sum(values) / len(values)

def process_select(data):
    return [value[0] for value in data]

def get_CIS_risk_damage(CIS_risk):
    impact_dimensions = int(CIS_risk.Impact_Dimensions[0])
    risk_score = int(CIS_risk.Risk_Score[0]) 
    uncertainty = int(CIS_risk.Uncertainty[0]) 
    risk_posture = CIS_risk.Risk_posture[0].lower()

    risk_posture_score = CIS_POSTURE_SCORE.get(risk_posture, 100)

    return (impact_dimensions * risk_score * risk_posture_score * uncertainty) / (10 * 9 * 100) 

def get_asset_damage(asset, CIS_risk_total_damage):
    asset_valuation = int(asset.Asset_Valuation[0]) 
    services_associated = len(asset.Services_associated)

    services_impact = 0.5 * (1 - pow(math.e, - services_associated / 5)) 

    return pow(CIS_risk_total_damage, 0.5) * asset_valuation * (services_impact + 0.5) / (10) 

def get_capability_score(capability, asset_total_damage):
    capability_score = int(capability.Score[0]) 
    capability_valuation = int(capability.Capability_Valuation[0]) 
    asset_total_damage = asset_total_damage / 100 

    new_score = capability_score * (100 - asset_total_damage * capability_valuation) / 100 
    return new_score

def get_action_score(action, capabilities_previous_total_score, capabilities_total_score):
    action_score = int(action.Score[0]) 
    if not capabilities_previous_total_score:
        return action_score

    new_score = action_score * capabilities_total_score / capabilities_previous_total_score
    return new_score

def get_task_score(task, action_previous_total_score, actions_total_score):
    task_score = int(task.Score[0]) 
    if not action_previous_total_score:
        return task_score

    new_score = task_score * actions_total_score / action_previous_total_score
    return new_score

