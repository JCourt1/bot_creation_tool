import React, { Component } from "react"
import axios from "axios";

var x = window.location.href.split("/");
let WEBSITEHOST = x[0] + "//" + x[2];

export default class Home extends Component {

  constructor(props) {
        super(props);

    }


    render(){
          return (

            <div id="About">

              <h2>About</h2>

                  <p>The Mental Health Triage Chatbot (MhtBot) was developed with the intention of assisting healthcare providers with mental health triage. </p>
                  <p> </p>

                  <h3>Guide to use</h3>

                          <h5>Patients</h5>
                              <p>The MhtBot stores user information including message history as well as PHQ-9 and GAD-7 scores.</p>

                          <h5>Interactive Training</h5>
                              <p>This tab allows the clinician to train the bot by interacting with it, and provides an interface for {"Rasa's"} interactive training system.
                                Concretely, the clinician speaks to the bot as if they were a patient, and at each step of the process,
                              information is displayed, such as:</p>

                                <div className="indented">

                                <h6>History Pane</h6>

                                    <p> The history of the conversation until the present moment, followed by: </p>
                                    <ul>
                                      <li>What the bot thought the clinician wanted to express (the {"\"intent\""} of his words)</li>
                                      <li>Any {"\"Entities\""} that have been identified (distinct things that we may want to recognise, such as the {"user's"} emotion (Happy, Sad, Anxious etc.)).</li>
                                    </ul>
                                    <p>Both intents and entities are identified using the {"bot's \"NLU\""} machine learning model.</p>


                                </div>

                                <div className="indented">

                                <h6>The prompt</h6>

                                    <p> In the centre of the screen, there is a prompt asking the clinician a question or telling them what to do next.
                                    For example, after the clinician has sent a message to the bot, the prompt will ask if the action that the bot wants to perform next is correct or not.
                                    (This prediction is the other place where Machine Learning is used, and is based on the identified intent of the message and the history of the conversation) </p>
                                    <p> A few options, with associated numbers.</p>

                                </div>

                                <div className="indented">

                                <h6>Actions / Intents table</h6>

                                    <p> In the event that the bot has predicted a wrong action, the prompt allows the clinician to point this out. </p>
                                    <p> The Actions or Intents chart provides a reference of actions or intents with associated indices.
                                    The idea here is that the clinician can nudge the bot in the right direction, and this input is used to improve the model of the bot.</p>

                                </div>

                          <h5>Custom Dialogues</h5>
                              <p>Custom Dialogues can be added here. This is useful for when strictly controlled dialogues are needed, such as fixed questionnaires.
                              The custom dialogue system supports branching based on particular {"\"intents\""}, and also moments where we need to enforce that the {"patient's"} response falls within a
                              range of fixed values.</p>

                              <p> The bot jumps from node to node at each step of the conversation. </p>
                              <p>These nodes can either be: </p>
                              <ul>
                                <li> Simple nodes, which just provide a response regardless of what the user said. </li>
                                <li> Validation nodes, which allow the clinician to enter a list of possible user inputs separated by forward slashes, and a bot response. </li>
                                <li> Tree nodes, which can be given branches to allow the conversation to fork based on the intent identified.
                                Tree nodes are just a collection of branches within which any other type of node can be nested (including other tree nodes)</li>
                              </ul>

                          <h5>Configure and Launch</h5>
                              <p>The Configure and Launch tab is used for reconfiguring the bot to use a certain dialogue model, and with a specific set of custom dialogues.</p>
                              <p>See the sections below for more detail on these.</p>


            </div>


          )

    }


}
