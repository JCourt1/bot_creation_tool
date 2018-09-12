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
