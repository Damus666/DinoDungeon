INTERACTION_DATA = {
    # TRADER
    0: {
        "type": "question",
        "text": ["Hi hero! Are you in search of a special key? I can help you!"],
        "actions": {
            "Show me [E]": {
                "type": "shop",
                "text": ["It's very rare and I only need the guard head"],
                "shop": [
                    [["Quartz Key", 1], ["Ogre Head", 1]],
                ],
                "actions": {
                    "Close [E]": "quit"
                }
            },
            "No thanks": "quit"
        }
    },
    # SMUGGLER
    1: {
        "type":"question",
        "text":["How did you get here?!","Anyways, wanna see the items I stole from the prison?"],
        "actions":{
            "Sure [E]": {
                "type":"shop",
                "text":["Take everything you need, I have lots."],
                "shop":[
                    [["Healing Potion",1],["coins",20]],[["Sword",1],["coins",50]],[["Knight Sword",1],["coins",200]]
                ],
                "actions": {
                    "Close [E]": "quit"
                }
            },
            "Not now":"quit"
        }
    },
    # KEY TRADER
    2:{
        "type":"question",
        "text":["You shouldn't be talking to me. What do you want?"],
        "actions":{
            "Do you have any key? [E]": {
                "type":"shop",
                "text":["Yes I do. I wonder how you got this information.","If you think the prices are high, think again."],
                "shop":[
                    [["Silver Key",1],["coins",200]],[["Prismarine Key",1],["coins",1000]]
                ],
                "actions": {
                    "I don't want them [E]":"quit"
                }
            },
            "Nothing":"quit"
        }
    }
}

ENEMY_DATA = {
    "masked_orc":(("Orc Mask",),"health_bar",12,"attack",80,{"damage":1}),
    "The Guard":(("Ogre Head","Mace"),"lock_room,boss_ui",100,"attack",110,{}),
    "Hell's Claws":(("Portal Key"),"lock_room,boss_ui",200,"attack",165,{}),
    "chort":([],"health_bar",9,"attack",100,{"damage":1}),
    "necromancer":([],"health_bar",15,"attack",60,{"damage":2}),
}
