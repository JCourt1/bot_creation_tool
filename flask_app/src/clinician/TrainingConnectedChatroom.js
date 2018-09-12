// @flow
import React, { Component } from "react";
import type { ElementRef } from "react";

import type { ChatMessage } from "./TrainingChatroom";
import Chatroom from "./TrainingChatroom";
import { sleep, uuidv4 } from "./utils";

const POLLING_INTERVAL = 1000;
const WAITING_TIMEOUT = 5000;
const MESSAGE_BLACKLIST = ["_restart"];

type ConnectedChatroomProps = {
  userId: string,
  host: string,
  title: string,
  addTrainingHints: (x: Array<ChatMessage>, y: (title: string, payload: string) => void, z: string) => void
};
type ConnectedChatroomState = {
  messages: Array<ChatMessage>,
  localMessages: Array<ChatMessage>,
  isOpen: boolean,
  waitingForBotResponse: boolean,
  messageCounter: number,
};

export default class ConnectedChatroom extends Component<
  ConnectedChatroomProps,
  ConnectedChatroomState,
> {
  state = {
    messages: [],
    localMessages: [],
    isOpen: true,
    waitingForBotResponse: false,
    messageCounter: -1,
    welcomeMessage: "Choose a model and start training!"
  };

  waitingForBotResponseTimer: ?TimeoutID = null;
  messageCounterInterval: ?IntervalID = null;
  _isMounted: boolean = false;
  chatroomRef: ?ElementRef<typeof Chatroom> = null;

  componentDidMount() {
    this._isMounted = true;
    this.poll();
  }

  componentDidUpdate(prevProps: ConnectedChatroomProps, prevState: ConnectedChatroomState) {
    if (!prevState.isOpen && this.state.isOpen) {
      this.fetchMessages();
    }
  }

  componentWillUnmount() {
    this._isMounted = false;
    if (this.waitingForBotResponseTimer != null) {
      window.clearTimeout(this.waitingForBotResponseTimer);
      this.waitingForBotResponseTimer = null;
    }
    if (this.messageCounterInterval != null) {
      window.clearInterval(this.messageCounterInterval);
      this.messageCounterInterval = null;
    }
  }

  sendMessage = async (messageText: string, payload?: string) => {
    if (messageText === "") return;

    const messageObj = {
      message: { type: "text", text: messageText },
      time: Date.now(),
      username: this.props.userId,
      uuid: uuidv4(),
    };

    if (!MESSAGE_BLACKLIST.includes(messageText)) {
      this.setState({
        localMessages: [...this.state.localMessages, messageObj],
        // Reveal all queued bot messages when the user sends a new message
        messageCounter: this.state.messages.length,
      });
    }

    const getParameters = {
      message: messageObj.message.text,
      payload: payload,
      uuid: messageObj.uuid,
    };
    const getParametersString = Object.keys(getParameters)
      .filter(k => getParameters[k] != null)
      .map(k => `${k}=${encodeURI(String(getParameters[k]))}`)
      .join("&");

    this.setState({ waitingForBotResponse: true });
    if (this.waitingForBotResponseTimer != null) {
      window.clearTimeout(this.waitingForBotResponseTimer);
    }
    this.waitingForBotResponseTimer = setTimeout(() => {
      if (this.state.messageCounter === this.state.messages.length) {
        this.setState({ waitingForBotResponse: false });
      }
    }, WAITING_TIMEOUT);
    await fetch(`${this.props.host}/conversations/${this.props.userId}/say?${getParametersString}`);

    if (window.ga != null) {
      window.ga("send", "event", "chat", "chat-message-sent");
    }
    await this.fetchMessages();
  };

  async fetchMessages() {



    try {
      var res = await fetch(
        `${this.props.host}/conversations/${this.props.userId}/log?nocache=${Date.now()}`,
      );

      var messages = await res.json();

    } catch(e) {
      // If the fetch failed, then we should get rid of all messages displayed.

      var TrainingFinished = "Training finished!";

      // if (this.state.welcomeMessage != TrainingFinished && this.state.messages.length > 0)

      if (this.state.messages.length > 0) {
          // console.log("fetch failed, so setting messages to empty");
          this.setState({messages: [], localMessages: [], waitingForBotResponse: false, messageCounter: 0, welcomeMessage: TrainingFinished});
      }

      return;

    }



    // var res = await axios(`${this.props.host}/conversations/${this.props.userId}/log?nocache=${Date.now()}`, {
    //   method: "get",
    //   withCredentials: true
    // });

    // const messages = await res.json();


    // Fix dates
    messages.forEach(m => {
      m.time = Date.parse(`${m.time}Z`);
    });


    sleep(20000);




    console.log(messages);

    console.log(messages.slice(0, Math.max(0, messageCounter)))



    // Remove redundant local messages
    const localMessages = this.state.localMessages.filter(
      m => !messages.some(n => n.uuid === m.uuid),
    );

    // Bot messages should be displayed in a queued manner. Not all at once
    let { messageCounter } = this.state;

    // Show all previous messages at the beginning of the session, e.g. page refresh
    if (messageCounter < 0) {
      messageCounter = messages.length;
    }
    if (messageCounter < messages.length) {
      // Increase the counter in every loop
      messageCounter++;

      // Set the counter to the last user message
      let lastUserMessageIndex = messages.length - 1;
      for (
        ;
        lastUserMessageIndex >= 0 && messages[lastUserMessageIndex].username === "bot";
        lastUserMessageIndex--
      );

      messageCounter = Math.max(lastUserMessageIndex, messageCounter);
    }

    // We might still be waiting on bot responses,
    // if there are unconfirmed user messages or missing replies

    // const waitingForBotResponse =
    //   (this.state.waitingForBotResponse && messageCounter !== messages.length) ||
    //   (localMessages.length > 0 && (messages.length === 0 // || messages[messages.length - 1].username !== "bot"
    // ));

    const waitingForBotResponse = (localMessages.length > 0 && (messages.length === 0 // || messages[messages.length - 1].username !== "bot"
  ));

  console.log(messages);

  console.log(messages.slice(0, Math.max(0, messageCounter)))

    this.setState({
      messages,
      localMessages,
      waitingForBotResponse,
      messageCounter,
    });
  }

  async poll() {
    while (this._isMounted) {
      try {
        if (this.state.isOpen) {
          await this.fetchMessages();
        }
      } catch (err) {
        // pass
      }
      await sleep(POLLING_INTERVAL);
    }
  }

  handleButtonClick = (message: string, payload: string) => {
    this.sendMessage(message, payload);
    if (window.ga != null) {
      window.ga("send", "event", "chat", "chat-button-click");
    }
  };

  handleToggleChat = () => {
    if (window.ga != null) {
      if (this.state.isOpen) {
        window.ga("send", "event", "chat", "chat-close");
      } else {
        window.ga("send", "event", "chat", "chat-open");
      }
    }
    this.setState({ isOpen: !this.state.isOpen });
  };

  render() {
    const { messages, localMessages, waitingForBotResponse, messageCounter } = this.state;

    const welcomeMessage =
      this.state.welcomeMessage != null
        ? {
            username: "bot",
            time: 0,
            message: {
              text: this.state.welcomeMessage,
              type: "text",
            },
            uuid: "9b9c4e2d-eb7f-4425-b23c-30c25bd7f507",
          }
        : null;

    const renderableMessages =
      welcomeMessage != null
        ? [welcomeMessage, ...messages.slice(0, Math.max(0, messageCounter)), ...localMessages]
        : [...messages.slice(0, Math.max(0, messageCounter)), ...localMessages];

    renderableMessages.sort((a, b) => a.time - b.time);

    return (
      <Chatroom
        messages={renderableMessages}
        title={this.props.title}
        showWaitingBubble={waitingForBotResponse}
        isOpen={this.state.isOpen}
        onToggleChat={this.handleToggleChat}
        onButtonClick={this.handleButtonClick}
        onSendMessage={this.sendMessage}
        addTrainingHints={this.props.addTrainingHints}
        ref={el => {
          this.chatroomRef = el;
        }}
      />
    );
  }
}
