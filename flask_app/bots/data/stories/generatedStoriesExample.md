## greet story
* greet
    - utter_greet


## goodbye story
* goodbye
    - utter_goodbye

## Propose end conversation
  - utter_proposeEnd
* affirm
  - utter_goodbye


## Feeling story (depressed)
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_feelingReply
    - utter_propose_questionnaire
* affirm
    - utter_phq9

## Feeling story (depressed but reject help)
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_feelingReply
    - utter_propose_questionnaire
* deny
    - respond_deny
    - utter_goodbye

## Feeling story (anxious)
* Feeling{"sentiment": "Anxious"}
    - slot{"sentiment": "Anxious"}
    - action_feelingReply
    - utter_propose_questionnaire
* affirm
    - utter_gad7

## Feeling story (anxious but reject help)
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_feelingReply
    - utter_propose_questionnaire
* deny
    - respond_deny
    - utter_goodbye

## Feeling story (happy)
* Feeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - action_feelingReply
  	- utter_goodbye

## thanks+goodbye story
* thanks+goodbye
    - utter_goodbye


## depressed_user
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_feelingReply
    - utter_propose_questionnaire
* affirm
    - utter_phq9
* selfharm
    - utter_self_harm_help
* thanks+goodbye
	- utter_thanks
	- utter_goodbye

## anxious_user
* greet
    - utter_greet
* Feeling{"sentiment": "Anxious"}
    - slot{"sentiment": "Anxious"}
    - action_feelingReply
    - utter_propose_questionnaire
* affirm
    - utter_gad7
* thanks+goodbye
	  - utter_thanks
	  - utter_goodbye

## happy_user
* greet
    - utter_greet
* Feeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - action_feelingReply
    - utter_propose_dialogues
* deny
    - respond_deny
    - utter_thanks
    - utter_goodbye

## happy user do dialogue
* greet
    - utter_greet
* Feeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - action_feelingReply
    - utter_propose_dialogues
* affirm
    - action_stop_and_show_dialogues
    - utter_thanks
    - utter_goodbye

## user wants dialogue
* requestDialogues
    - action_stop_and_show_dialogues
    - utter_thanks
    - utter_goodbye

## hit_fallback
  - utter_fallback
* thanks
  - utter_thanks
## Generated Story -2519023318063592936
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - export

## Generated Story -9070006173816193443
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_feelingReply
    - export

## Generated Story -6893542743914969816
* greet
    - utter_greet
    - export

## Generated Story 7708824436509212679
* greet
    - utter_greet
    - export

## Generated Story 3526065460873820557
* greet
    - utter_greet
    - export

## Generated Story 5312203251270440967
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - export

## Generated Story 1952720282203616600
* greet
    - utter_greet
    - export

## Generated Story 5859742558480677161
* greet
    - utter_greet
    - export

## Generated Story 356158027713223833
* greet
    - utter_greet
    - export

## Generated Story -5006494137491397313
* greet
    - utter_greet
    - export

## Generated Story 9071326413276404335
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - export

## Generated Story -1835451519585442299
* greet
    - utter_greet
* selfharm
    - export

## Generated Story 500354867410363777
* greet
    - export

## Generated Story 1519275805655522930
* goodbye
* affirm{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_greet
* selfharm
    - utter_phq9
* selfharm
    - export

## Generated Story 1215026074641325445
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - action_feelingReply
    - export

## Generated Story -779359945752626813
* greet
    - utter_greet
* Feeling
    - export

## Generated Story -6761932487077394827
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - export

## Generated Story 4972519417094523764
* greet
    - utter_greet
* Feeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - export

