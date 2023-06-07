from owlready2 import *
import matplotlib.pyplot as plt
import numpy as np
import os
from mdutils.mdutils import MdUtils
from md2pdf.core import md2pdf
import datetime
from ONTOLOGIATFMGESTION import *

DPI = 96
GRAPH_WIDTH = 1080
GRAPH_HEIGHT = 290

date = datetime.datetime.now()
date = date.strftime("%c")

def update_ontology_scores(onto):
    CIS_risks = list(onto.CIS_Risk.instances())
    CIS_risks_damage = {
        get_individual_name(CIS_risk): get_CIS_risk_damage(CIS_risk) 
            for CIS_risk in CIS_risks
    }

    assets = list(onto.Asset.instances())
    assets_damage = {get_individual_name(asset): 0 for asset in assets}
    for asset in assets:
        asset_name = get_individual_name(asset)

        get_CIS_risk_query = create_select(
            select="?cis_risk",
            where=f"""
                ?asset rdf:type onto:Asset .
                ?asset onto:isDamagedBy ?cis_risk .
                FILTER(?asset = onto:{ asset_name }) .              
            """ 
        )
        asset_CIS_risks = list(default_world.sparql(get_CIS_risk_query))
        asset_CIS_risks = process_select(asset_CIS_risks)
        asset_CIS_risks_damage = [CIS_risks_damage[get_individual_name(CIS_risk)] for CIS_risk in asset_CIS_risks]
        asset_inherited_damage = get_median(asset_CIS_risks_damage)

        assets_damage[get_individual_name(asset)] = get_asset_damage(asset, asset_inherited_damage)

    capabilities = list(onto.Capability.instances())
    capabilities_previous_scores = {
        get_individual_name(capability) : capability.Score[0] 
            for capability in capabilities
    }
    for capability in capabilities:
        capability_name = get_individual_name(capability)
        

        get_assets_query = create_select(
            select="?asset",
            where=f"""
                ?asset rdf:type onto:Asset .
                ?asset onto:gives onto:{ capability_name } .
            """
        )
        capability_assets = list(default_world.sparql(get_assets_query))
        capability_assets = process_select(capability_assets)
        capability_assets_damage = [assets_damage[get_individual_name(asset)] for asset in capability_assets]
        capability_total_damage = get_median(capability_assets_damage)

        capability.Score = [get_capability_score(capability, capability_total_damage)]

    actions = list(onto.Action.instances())
    actions_previous_scores = {
        get_individual_name(action) : action.Score[0] 
            for action in actions
    }
    for action in actions:
        action_name = get_individual_name(action)

        get_capabilities_query = create_select(
            select="?capability",
            where=f"""
                ?capability rdf:type onto:Capability .
                ?capability onto:enables onto:{ action_name } .
            """            
        )
        action_capabilities = list(default_world.sparql(get_capabilities_query))
        action_capabilities = process_select(action_capabilities)
        action_capabilities_score = [capability.Score[0] for capability in action_capabilities]
        capabilities_previous_total_score = get_median([
            capabilities_previous_scores[get_individual_name(capability)]
                for capability in action_capabilities
        ])
        capabilities_total_score = get_median(action_capabilities_score)

        action.Score = [get_action_score(action, capabilities_previous_total_score, capabilities_total_score)]

    tasks = list(onto.Task.instances())
    for task in tasks:
        task_name = get_individual_name(task)

        get_actions_query = create_select(
            select="?action",
            where=f"""
                ?task rdf:type onto:Task .
                ?task onto:has ?action .
                FILTER(?task = onto:{ task_name }) .              
            """ 
        )
        task_actions = list(default_world.sparql(get_actions_query))
        task_actions = process_select(task_actions)
        task_actions_score = [action.Score[0] for action in task_actions]
        action_previous_total_score = get_median([
            actions_previous_scores[get_individual_name(action)]
                for action in task_actions
        ])
        actions_total_score = get_median(task_actions_score)

        task_prev_score = task.Score[0]
        task.Score = [get_task_score(task, action_previous_total_score, actions_total_score)]
        
        x = [task.Score[0], task_prev_score - task.Score[0]]
        colors = ["#2eac9f", "#f5bd05"]
       
        plt.figure(figsize=(GRAPH_WIDTH / DPI, (GRAPH_HEIGHT - 50) / DPI), dpi=DPI)
        plt.pie(x, colors=colors, labels=["New score", ""], startangle = 90)
        plt.title("Task score variation")
        plt.savefig(f"./graphs/{ task_name }.png", dpi=DPI)
        plt.close()

        get_linked_data_query = create_select(
            select="?cis_risk ?asset ?capability ?action",
            where=f"""
                ?task rdf:type onto:Task .
                FILTER(?task = onto:{ task_name }) .
                ?task onto:has ?action .
                ?capability rdf:type onto:Capability .
                ?capability onto:enables ?action .
                ?asset rdf:type onto:Asset .
                ?asset onto:gives ?capability .
                ?asset onto:isDamagedBy ?cis_risk .
            """ 
        )

        CIS_risks, assets, capabilities, actions = set(), set(), set(), set()
        for data in default_world.sparql(get_linked_data_query):
            CIS_risks.add(data[0])
            assets.add(data[1])
            capabilities.add(data[2])
            actions.add(data[3])
        
        CIS_risks = sorted(CIS_risks, key=lambda x: get_individual_name(x))
        assets = sorted(assets, key=lambda x: get_individual_name(x))
        capabilities = sorted(capabilities, key=lambda x: get_individual_name(x))
        actions = sorted(actions, key=lambda x: get_individual_name(x))

        y = [CIS_risks_damage[get_individual_name(CIS_risk)] for CIS_risk in CIS_risks]
        x = [get_individual_name(CIS_risk) for CIS_risk in CIS_risks]

        plt.figure(figsize=(GRAPH_WIDTH / DPI, GRAPH_HEIGHT / DPI), dpi=DPI)
        plt.scatter(x, y, color="#2da79a")
        plt.plot(x, y, color="#2da79a")
        #plt.xlabel("CIS Risks")
        plt.ylabel("Damage")
        plt.title("CIS Risks Analysis")
        plt.savefig(f"./graphs/{ task_name }-CIS_Risks.png", dpi=DPI)
        plt.close()

        y = [assets_damage[get_individual_name(asset)] for asset in assets]
        x = [get_individual_name(asset) for asset in assets]

        plt.figure(figsize=(GRAPH_WIDTH / DPI, GRAPH_HEIGHT / DPI), dpi=DPI)
        plt.scatter(x, y, color="#2da79a")
        plt.plot(x, y, color="#2da79a")
        #plt.xlabel("Assets")
        plt.ylabel("Damage")
        plt.title("Assets Analysis")
        plt.savefig(f"./graphs/{ task_name }-Assets.png", dpi=DPI)
        plt.close()

        x = [get_individual_name(capability) for capability in capabilities]
        old_y = [capabilities_previous_scores[get_individual_name(capability)] for capability in capabilities]
        new_y = [capability.Score[0] for capability in capabilities]
          
        plt.figure(figsize=(GRAPH_WIDTH / DPI, GRAPH_HEIGHT / DPI), dpi=DPI)

        x_axis = np.arange(len(x)) 
        plt.bar(x_axis - 0.2, old_y, 0.4, label = 'Old Score', color="#2da79a")
        plt.bar(x_axis + 0.2, new_y, 0.4, label = 'New Score', color="#f5bd05")
   
        plt.xticks(x_axis, x)  
        #plt.xlabel("Capabilities")
        plt.ylabel("Scores")
        plt.title("Capabilities Analysis")
        plt.legend()
        plt.savefig(f"./graphs/{ task_name }-Capabilities.png", dpi=DPI)
        plt.close()

        x = [get_individual_name(action) for action in actions]
        old_y = [actions_previous_scores[get_individual_name(action)] for action in actions]
        new_y = [action.Score[0] for action in actions]
          
        plt.figure(figsize=(GRAPH_WIDTH / DPI, GRAPH_HEIGHT / DPI), dpi=DPI)

        x_axis = np.arange(len(x)) 
        plt.bar(x_axis - 0.2, old_y, 0.4, label = 'Old Score', color="#2da79a")
        plt.bar(x_axis + 0.2, new_y, 0.4, label = 'New Score', color="#f5bd05")

        plt.xticks(x_axis, x)  
        #plt.xlabel("Actions")
        plt.ylabel("Scores")
        plt.title("Actions Analysis")
        plt.legend()
        plt.savefig(f"./graphs/{ task_name }-Actions.png", dpi=DPI)
        plt.close()

def create_MI_risks(onto):
    tasks = list(onto.Task.instances())
    for task in tasks:
        task_name = get_individual_name(task)

        get_CIS_risk_query = create_select(
            select="?cis_risk",
            where=f"""
                ?task rdf:type onto:Task .
                FILTER(?task = onto:{ task_name }) .
                ?task onto:has ?action .
                ?capability rdf:type onto:Capability .
                ?capability onto:enables ?action .
                ?asset rdf:type onto:Asset .
                ?asset onto:gives ?capability .
                ?asset onto:isDamagedBy ?cis_risk .
            """ 
        )
        linked_CIS_risks = set(data[0] for data in default_world.sparql(get_CIS_risk_query))

        if linked_CIS_risks:
            MI_risk_name = f"MI_Risk_{ task_name }"
            onto.MI_Risk(MI_risk_name)

            set_relations = create_insert(
                insert="""
                """ + "\n".join(
                    f"?mi_risk onto:canBeCreatedBy onto:{ get_individual_name(CIS_risk) } ." 
                        for CIS_risk in linked_CIS_risks
                ) + """
                    ?task onto:isRelatedTo ?mi_risk .
                """,
                where=f"""
                    ?mi_risk rdf:type onto:MI_Risk .
                    FILTER(?mi_risk = onto:{ MI_risk_name })
                    ?task rdf:type onto:Task . 
                    FILTER(?task = onto:{ task_name })    
                """
            )
            default_world.sparql(set_relations)

    MI_risks = list(onto.MI_Risk.instances())
    for MI_risk in MI_risks:
        MI_risk.Card_Creation.append(date)

def create_effect(onto):
    actions = list(onto.Action.instances())
    for action in actions:
        action_name = get_individual_name(action)

        effect_name = f"Effect_{ action_name }"
        onto.Effect(effect_name)
        

        set_relations = create_insert(
            insert="""
                ?action onto:resultsIn ?effect .
            """,
            where=f"""
                ?action rdf:type onto:Action .
                FILTER(?action = onto:{ action_name })
                ?effect rdf:type onto:Effect . 
                FILTER(?effect = onto:{ effect_name })
            """
        )
        default_world.sparql(set_relations)

    effects = list(onto.Effect.instances())
    for effect in effects:
        effect.Card_Creation.append(date)

def generate_report(task):
    task_name = get_individual_name(task)
    absolute_path = os.path.abspath('.')

    get_linked_data_query = create_select(
        select="?cis_risk ?asset ?capability ?action",
        where=f"""
            ?task rdf:type onto:Task .
            FILTER(?task = onto:{ task_name }) .
            ?task onto:has ?action .
            ?capability rdf:type onto:Capability .
            ?capability onto:enables ?action .
            ?asset rdf:type onto:Asset .
            ?asset onto:gives ?capability .
            ?asset onto:isDamagedBy ?cis_risk .
        """ 
    )

    CIS_risks, assets, capabilities, actions = set(), set(), set(), set()
    for data in default_world.sparql(get_linked_data_query):
        CIS_risks.add(data[0])
        assets.add(data[1])
        capabilities.add(data[2])
        actions.add(data[3])
    
    CIS_risks = sorted(CIS_risks, key=lambda x: get_individual_name(x))
    assets = sorted(assets, key=lambda x: get_individual_name(x))
    capabilities = sorted(capabilities, key=lambda x: get_individual_name(x))
    actions = sorted(actions, key=lambda x: get_individual_name(x))

    if not len(actions):
        return

    if not os.path.isdir('./reports'):
        os.mkdir('reports')
    
    fileOut = f"report-{ task_name }"

    mdFile = MdUtils(file_name=fileOut)

    report_title = f"{ task_name } report"
    if task.Description:
        report_title = f"{ report_title } - { task.Description[0] }"
    
    mdFile.new_header(level=1, title=f"{ report_title }")

    mdFile.new_line(f"![test](./graphs/{ task_name }.png)")
    mdFile.new_line(f"- **New score:** { round(task.Score[0], 2) }")
    MI_risk = task.isRelatedTo
    MI_risk_name = get_individual_name(MI_risk[0]).replace("_", "\_")
    mdFile.new_line(f"- **Related MI Risk:** { MI_risk_name }")

    mdFile.new_header(level=2, title='CIS Risks')
    mdFile.new_header(level=3, title='Graphs')
    mdFile.new_line(f"![test](./graphs/{ task_name }-CIS_Risks.png)")

    mdFile.new_header(level=2, title='Assets')
    mdFile.new_header(level=3, title='Graphs')
    mdFile.new_line(f"![test](./graphs/{ task_name }-Assets.png)")
    mdFile.new_header(level=3, title='Relations')
    for asset in assets:
        asset_name = get_individual_name(asset)
        get_CIS_risk_query = create_select(
            select="?cis_risk",
            where=f"""
                ?asset rdf:type onto:Asset .
                ?asset onto:isDamagedBy ?cis_risk .
                FILTER(?asset = onto:{ asset_name }) .              
            """ 
        )
        asset_CIS_risks = list(default_world.sparql(get_CIS_risk_query))
        CIS_risks_names  = [get_individual_name(CIS_risk[0]).replace("_", "\_") for CIS_risk in asset_CIS_risks]
        mdFile.new_line(f"- **{ asset_name }:** { ', '.join(CIS_risks_names) }")
    mdFile.write("\n")

    mdFile.new_header(level=2, title='Capabilities')
    mdFile.new_header(level=3, title='Graphs')
    mdFile.new_line(f"![test](./graphs/{ task_name }-Capabilities.png)")
    mdFile.new_header(level=3, title='Relations')
    for capability in capabilities:
        capability_name = get_individual_name(capability)
        get_assets_query = create_select(
            select="?asset",
            where=f"""
                ?asset rdf:type onto:Asset .
                ?asset onto:gives onto:{ capability_name } .
            """
        )
        capability_assets = list(default_world.sparql(get_assets_query))
        assets_names  = [get_individual_name(asset[0]).replace("_", "\_") for asset in capability_assets]
        mdFile.new_line(f"- **{ capability_name }:** { ', '.join(assets_names) }")
    mdFile.write("\n")

    mdFile.new_header(level=2, title='Actions')
    mdFile.new_header(level=3, title='Graphs')
    mdFile.new_line(f"![test](./graphs/{ task_name }-Actions.png)")
    mdFile.new_header(level=3, title='Relations')
    for action in actions:
        action_name = get_individual_name(action)
        get_capabilities_query = create_select(
            select="?capability",
            where=f"""
                ?capability rdf:type onto:Capability .
                ?capability onto:enables onto:{ action_name } .
            """            
        )
        action_capabilities = list(default_world.sparql(get_capabilities_query))
        capabilities_names  = [get_individual_name(capability[0]).replace("_", "\_") for capability in action_capabilities]
        mdFile.new_line(f"- **{ action_name }:** { ', '.join(capabilities_names) }")
    mdFile.write("\n")

    mdFile.create_md_file()

    md2pdf(f"./reports/{ fileOut }.pdf",
        md_content=None,
        md_file_path=f"{ fileOut }.md",
        css_file_path="informe.css",
        base_url=absolute_path + "/")

    
    os.remove(f"./{ fileOut }.md")

def analyze_ontology(onto):
    if not os.path.isdir('./graphs'):
        os.mkdir('graphs')

    update_ontology_scores(onto)
    create_MI_risks(onto)
    create_effect(onto)

    tasks = list(onto.Task.instances())
    for task in tasks:
        generate_report(task)

def main():
    onto = get_ontology("ONTOLOGY").load()
    with onto:
        analyze_ontology(onto)
        onto.save(file = "ONTOLOGY", format = "rdfxml")

if __name__ == "__main__":
    main()
