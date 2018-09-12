## greet story
* greet
    - utter_greet

## greet and smalltalk
* greet
    - utter_greet
* askHowBotIs
  - respond_howareyou


## goodbye story
* goodbye
    - action_say_goodbye


## Feeling story (depressed)
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - reply_to_feeling
    - utter_propose_questionnaire
* affirm
    - respond_affirm
    - show_phq9

## Feeling story (depressed but reject help)
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - reply_to_feeling
    - utter_propose_questionnaire
* deny
    - respond_deny
    - utter_ask_if_end
* deny
    - utter_propose_dialogues

## Feeling story (anxious)
* expressFeeling{"sentiment": "Anxious"}
    - slot{"sentiment": "Anxious"}
    - reply_to_feeling
    - utter_propose_questionnaire
* affirm
    - respond_affirm
    - show_gad7

## Feeling story (anxious but reject help)
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - reply_to_feeling
    - utter_propose_questionnaire
* deny
    - respond_deny
    - utter_ask_if_end
* affirm
    - action_say_goodbye

## Feeling story (anxious, reject help, but still talking)
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - reply_to_feeling
    - utter_propose_questionnaire
* deny
    - respond_deny
    - utter_ask_if_end
* deny
    - utter_askCause

## Feeling story (happy and stop)
* expressFeeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - reply_to_feeling
    - utter_ask_if_end
* affirm
    - action_say_goodbye

## Feeling story (happy but continue)
* expressFeeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - reply_to_feeling
    - utter_ask_if_end
* deny
    - utter_propose_dialogues


## Self harm story
* expressSelfHarm
  - action_log_self_harm

## depressed_user
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - reply_to_feeling
    - utter_propose_questionnaire
* affirm
    - show_phq9
* expressSelfHarm
    - action_log_self_harm
    - utter_propose_dialogues
* affirm
	- show_dialogues

## Repeat dialogues
* requestDialogues
  - show_dialogues
* expressFeeling
  - utter_repropose_dialogs
* affirm
  - show_dialogues

## anxious_user
* greet
    - utter_greet
* expressFeeling{"sentiment": "Anxious"}
    - slot{"sentiment": "Anxious"}
    - reply_to_feeling
    - utter_propose_questionnaire
* affirm
    - show_gad7
* thanks
	  - utter_thanks
	  - utter_ask_if_end
* affirm
    - action_say_goodbye

## happy_user
* greet
    - utter_greet
* expressFeeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - reply_to_feeling
    - utter_propose_dialogues
* deny
    - respond_deny

## happy user do dialogue
* greet
    - utter_greet
* expressFeeling{"sentiment": "Happy"}
    - slot{"sentiment": "Happy"}
    - reply_to_feeling
    - utter_propose_dialogues
* affirm
    - show_dialogues

## user wants dialogue
* requestDialogues
    - show_dialogues

## hit_fallback
  - utter_fallback
* thanks
  - utter_thanks

## hit_fallback
  - utter_fallback
* askWhatCanBotDo
  - utter_propose_dialogues


## smalltalk
* askHowBotIs
  - respond_howareyou

## askForGuidance
* askForGuidance
  - utter_askCause
* expressFeeling
  - show_dialogues
## Generated Story 4988786834187651284
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - reply_to_feeling
    - utter_propose_questionnaire
* deny
    - respond_deny
    - utter_ask_if_end
* affirm
    - utter_propose_questionnaire
    - export
## Generated Story -6572142009576406
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story -6637550843904221991
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story 4610319249030346676
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story -4336981429848129647
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story 5468130216255224660
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story 8325088979092269149
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story -755158556569310161
* greet
    - utter_greet
* expressFeeling{"sentiment": "Depressed"}
    - slot{"sentiment": "Depressed"}
    - utter_greet
    - export

## Generated Story 6076231003743183929
* greet
    - utter_thanks
* expressFeeling
    - export

