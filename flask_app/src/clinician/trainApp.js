// @flow
import type { ChatMessage } from "./TrainingChatroom";

import "unfetch/polyfill";
import "babel-polyfill";
import React from "react";
import ReactDOM from "react-dom";
import type { ElementRef } from "react";

import Chatroom from "./TrainingChatroom";
import TrainingHints from "./TrainingHints";

import { noop, sleep, uuidv4 } from "./utils";
import ConnectedChatroom from "./TrainingConnectedChatroom";

import DialogueForm from "./components/DialogueForm";
import BotConfigForm from "./components/BotConfigForm";
import PatientInfo from "./components/PatientInfo";
import Home from "./components/Home";
import ControlRoom from "./components/ControlRoom";

import Button from '@material-ui/core/Button'; /// https://material-ui.com/getting-started/usage/

import PropTypes from 'prop-types';
// import Tabs from '@material-ui/core/Tabs';
// import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import AppBar from '@material-ui/core/AppBar';


import { Tabs, Tab, TabPanel, TabList } from 'react-web-tabs';

const USERID_STORAGE_KEY = "simple-chatroom-cid";

type ChatroomOptions = {
  host: string,
  title?: string,
  welcomeMessage?: string,
  container: HTMLElement
};

// let BOTHOST = window.sessionStorage.getItem("hostForBot");
////
// var x = window.location.href.split("/");
// let BOTHOST = x[0] + "//" + x[2] + ":5002";
let BOTHOST = location.protocol + "//" + location.hostname + ":5002";
////
let sessionUserId = window.sessionStorage.getItem(USERID_STORAGE_KEY);

if (sessionUserId == null) {
  sessionUserId = uuidv4();
  window.sessionStorage.setItem(USERID_STORAGE_KEY, "cliniciansID");
}

function TabContainer(props) {
  return (
    <Typography component="div" style={{ padding: 8 * 3 }}>
      {props.children}
    </Typography>
  );
}

TabContainer.propTypes = {
  children: PropTypes.node.isRequired,
};


class App extends React.Component {


    constructor() {
        super();

        this.state = {
            thintsHistory: [],
            thintsBotAction: [],
            thintsActionList: [],
            thintsKeyOptions: [],
            onButtonClick: function() {return},
            TurnPBotOff: false,
            TurnTBotOff: false,
            dialogue_files: window.setupData.dialogue_files ,
            d_models: window.setupData.d_models,
            value: 0
        };
        this.addTrainingHints = this.addTrainingHints.bind(this);
        this.OnOffSwitch = this.OnOffSwitch.bind(this);
        this.setDialogueFiles = this.setDialogueFiles.bind(this);
        this.setDModels = this.setDModels.bind(this);

        // The function that will need to be called is:
        //
        // this.setState({
        //      messages: [...this.state.trainingHints, trainingHint]
        // })

    }

    // userId={this.state.sessionUserId}

    tabClick = (event, value) => {
      this.setState({ value });
    };

    addTrainingHints(trainhints, onButtonClick, destination) {

      if (destination === "thintHistory") {
        this.setState({thintsHistory: trainhints, onButtonClick: onButtonClick});
      } else if (destination === "thintBotAction") {
        this.setState({thintsBotAction: trainhints, onButtonClick: onButtonClick});
      } else if (destination === "thintActionList") {
        this.setState({thintsActionList: trainhints, onButtonClick: onButtonClick});
      } else if (destination === "thintKeyOptions") {
        this.setState({thintsKeyOptions: trainhints, onButtonClick: onButtonClick});
      }

    }

    OnOffSwitch(arg) {

      if (arg == "TBot") {
        this.setState({TurnTBotOff: true});
      } else if (arg == "PBot"){
        this.setState({TurnPBotOff: true});
      } else {
        this.setState({TurnTBotOff: false, TurnPBotOff: false})
      }

    }

    setDialogueFiles(array) {
      this.setState({dialogue_files: array});
    }

    setDModels(array) {
      this.setState({d_models: array});
      this.forceUpdate();
    }

    render() {

        const { value } = this.state.value;



        return (


                <Tabs className="wholeApp" defaultTab="vertical-tab-one" vertical>
                    <TabList className="sideBar">
                          <Tab tabFor="vertical-tab-one">Home</Tab>
                          <Tab tabFor="vertical-tab-two">Patients</Tab>
                          <Tab tabFor="vertical-tab-three">Interactive Training</Tab>
                          <Tab tabFor="vertical-tab-four">Custom Dialogues</Tab>
                          <Tab tabFor="vertical-tab-five">Configure and Launch</Tab>
                    </TabList>
                    <TabPanel className="tpanel" tabId="vertical-tab-one">
                              <Home />
                    </TabPanel>
                    <TabPanel className="tpanel" tabId="vertical-tab-two">
                              <PatientInfo />
                    </TabPanel>
                    <TabPanel className="tpanel" tabId="vertical-tab-three">

                              <div id="chatAndTraining">

                                <BotConfigForm
                                  OnOffFlag={this.state.TurnTBotOff}
                                  OnOffSwitch={this.OnOffSwitch}
                                  d_models={this.state.d_models}
                                  setDModels={this.setDModels}
                                />

                                <TrainingHints role="ActionList" title="Index" trainingHints={this.state.thintsActionList} onButtonClick={this.state.onButtonClick}/>

                                <div id="chat-container">
                                    <ConnectedChatroom

                                      userId={sessionUserId}
                                      host= {BOTHOST}
                                      title={""}
                                      addTrainingHints = {this.addTrainingHints}
                                    />
                                </div>

                                <TrainingHints role="History" title="History" trainingHints={this.state.thintsHistory} onButtonClick={this.state.onButtonClick}/>

                                <TrainingHints role="BotAction" title="* * * * * * *" trainingHints={this.state.thintsBotAction} onButtonClick={this.state.onButtonClick}/>

                                <TrainingHints role="KeyOptions" title="Options" trainingHints={this.state.thintsKeyOptions} onButtonClick={this.state.onButtonClick}/>
                                </div>

                    </TabPanel>
                    <TabPanel className="tpanel" tabId="vertical-tab-four">
                          <DialogueForm
                            dialogue_files={this.state.dialogue_files}
                            setDialogueFiles={this.setDialogueFiles}
                          />
                    </TabPanel>
                    <TabPanel className="tpanel" tabId="vertical-tab-five">
                              <ControlRoom
                                OnOffFlag={this.state.TurnPBotOff}
                                OnOffSwitch={this.OnOffSwitch}
                                dialogue_files={this.state.dialogue_files}
                                d_models={this.state.d_models}
                              />
                    </TabPanel>
                </Tabs>


        );
    }
}


export default App


// <div className="tabStyles">
//   <AppBar position="static">
//     <Tabs value={value} onChange={this.tabClick}>
//       <Tab label="Item One" />
//       <Tab label="Item Two" />
//       <Tab label="Item Three" href="#basic-tabs" />
//     </Tabs>
//   </AppBar>
//   {value === 0 && <TabContainer>Item One</TabContainer>}
//   {value === 1 && <TabContainer>Item Two</TabContainer>}
//   {value === 2 && <TabContainer>Item Three</TabContainer>}
// </div>
