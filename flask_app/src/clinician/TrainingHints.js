import React from "react";
import ReactDOM from "react-dom";
import Message, { MessageTime } from "./Message";



class TrainingHints extends React.Component {

  componentDidMount() {
    this.scrollToBottom();
  }

  componentDidUpdate() {
    this.scrollToBottom();
  }

  scrollToBottom() {
    // this.thintsref.scrollIntoView({ behavior: 'smooth' });
    this.thintsref.scrollTop = this.thintsref.scrollHeight;
  }


  render() {
      const { trainingHints } = this.props;

      if (trainingHints.length > 0) {
        var f = (trainingHint) => {
          return (
            <Message chat={trainingHint} key={1} onButtonClick={this.props.onButtonClick} />
          )
        }

        console.log("Training hints = ");
        console.log(trainingHints);

        console.log("THIS IS THE LAST TRAINING HINT FOR THIS BIT:");

        console.log(trainingHints[trainingHints.length - 1]);


        return (

          <div className={"training-hints " + (this.props.trainingHints.length == 0 || this.props.role != "ActionList" ? 'hideIt' : 'highlightIt')} id= {this.props.role + "Container"} ref={el => { this.thintsref = el; }}>

              <div id= {this.props.role + "Wrapper"}>
              <h2>{this.props.title}</h2>

              <ul> {



                f(trainingHints[trainingHints.length - 1])

            }
              </ul>
              </div>
          </div>
        )

      } else {

        return (

          <div className={"training-hints " + (this.props.trainingHints.length == 0 || this.props.role != "ActionList" ? 'hideIt' : 'highlightIt')} id= {this.props.role + "Container"} ref={el => { this.thintsref = el; }}>

              <div id= {this.props.role + "Wrapper"}>
              <h2>{this.props.title}</h2>

              <ul> {

              //   trainingHints.map((trainingHint, index) => {
              //   return (
              //     <Message chat={trainingHint} key={index} onButtonClick={this.props.onButtonClick} />
              //     // <TrainingHint key={index} text={trainingHint} />
              //   )
              // })

            }
              </ul>
              </div>
          </div>
        )

      }


  }
}

export default TrainingHints
