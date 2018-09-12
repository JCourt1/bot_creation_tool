// @flow
import "unfetch/polyfill";
import "babel-polyfill";
import classnames from "classnames";
import React from 'react';
import ReactDOM from 'react-dom';
import type { ChatMessage } from "./Chatroom";
import Chatroom from "./Chatroom";
import { noop, sleep, uuidv4 } from "./utils";
import ConnectedChatroom from "./ConnectedChatroom";

const USERID_STORAGE_KEY = "simple-chatroom-cid";

// var x = window.location.href.split("/");
// let BOTHOST = x[0] + "//" + x[2] + ":5002";
let BOTHOST = location.protocol + "//" + location.hostname + ":5002";

type ChatroomOptions = {
  host: string,
  title?: string,
  welcomeMessage?: string,
  container: HTMLElement
};

function getCookies() {
    return document.cookie.split("; ").reduce(function(cookies, token){
        // split key=value into array
        var pair = token.split("=");
        // assign value (1) as object's key with (0)
        cookies[pair[0]] = decodeURIComponent(pair[1]);
        // pass through the key-value store
        return cookies;
    }, { /* start with empty "cookies" object */ });
}

function getCookie(name) {
    return getCookies()[name];
}

// let sessionUserId = window.sessionStorage.getItem(USERID_STORAGE_KEY);
//
// if (sessionUserId == null) {
//   sessionUserId = uuidv4();
//   window.sessionStorage.setItem(USERID_STORAGE_KEY, sessionUserId);
// }

let conversationId = getCookie("conversation_id");
let userId = getCookie("user_id");


class App extends React.Component {
    constructor() {
        super()
        this.state = {
            onButtonClick: function() {return}
        }

        // The function that will need to be called is:
        //
        // this.setState({
        //      messages: [...this.state.trainingHints, trainingHint]
        // })

    }

    // userId={this.state.sessionUserId}

    render() {
        return (
            <div className="wholeApp">
                  <div id="chat-container">
                      <ConnectedChatroom

                        userId={conversationId}
                        host= {BOTHOST}
                        title={""}
                        welcomeMessage={"Hello!"}
                      />
                  </div>
            </div>

        );
    }
}


ReactDOM.render(<App />, document.getElementById('app'));
