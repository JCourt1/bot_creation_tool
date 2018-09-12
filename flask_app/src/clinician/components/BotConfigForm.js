import React, { Component } from "react";
import Button from '@material-ui/core/Button';
import axios from "axios";

var x = window.location.href.split("/");
let WEBSITEHOST = x[0] + "//" + x[2];
var DEFAULT_D_MODEL = "default";


export default class BotConfigForm extends Component {

  constructor(props) {
        super(props);
        this.state = { d_models: this.props.d_models || null, chosenModel: null, tbotOff: null };
        this.handleSelectModel = this.handleSelectModel.bind(this);
        this.startTraining = this.startTraining.bind(this);

  }

  componentDidMount(){

    fetch(`${WEBSITEHOST}/checktbotoff`).then((response) => {
          response.json().then((data) => {
            this.setState({tbotOff: data});
            console.log(this.state.tbotOff);
      });
    });

  }

  componentWillReceiveProps(nextProps){
    this.setState({d_models: nextProps.d_models})
  }

  handleSelectModel(event) {
    event.preventDefault();
    this.setState({chosenModel: event.target.value})

  }

  startTraining = () => {

    let formData = new FormData(document.getElementById("trainForm"));

    let base_model = formData.get("base_model");
    let new_model = formData.get("new_model");
    let bad_values = ['', 'None', undefined, null];
    let new_model_is_valid = /^[a-zA-Z0-9-_]+$/.test(new_model);

    console.log(base_model);
    console.log(new_model);

    if ( (bad_values.includes(base_model) || bad_values.includes(new_model)) && this.state.tbotOff) {
      alert("Choose settings before launching training.");
    } else if (new_model == DEFAULT_D_MODEL) {
      alert("Cannot overwrite the default model");
    } else if (!new_model_is_valid) {
      alert("The new model entered is invalid");
    } else {
      axios({
        method: 'post',
        url: `${WEBSITEHOST}/toggleTrain`,
        data: formData
      }).then((response) => {
        if (response.data == "success") {
          let prevState = this.state.tbotOff;
          this.setState({tbotOff: !this.state.tbotOff});
          this.props.OnOffSwitch("PBot");

          if (prevState == false) {
            fetch(`${WEBSITEHOST}/updateDModelsList`).then((response) => {
                response.json().then((data) => {
                    console.log(data);
                    console.log("ADAWHDHAWD");
                    var d_models = data;
                    this.props.setDModels(d_models);
                });
            });
          }


        } else {
          alert("Something went wrong.");
        }

      });
    }

  }


  render(){

            if (this.props.OnOffFlag) {
              this.setState({tbotOff: true});
              this.props.OnOffSwitch("reset");
            }

            return (

              <div id="buttonsAndInstructions">

                  <div id="statusContainer">

                  <div id="trainingBotStatus" className= {this.state.tbotOff ? 'off' : 'glowing'}></div>

                  <p>{this.state.tbotOff ? "Switch training bot on" : "Training is on"}</p>
                  </div>

                  <form method="post" id="trainForm">

                          <input className="Hidden" type="text" name="base_model" value={this.state.chosenModel || ''}/>


                          <select id="oldm" onChange={this.handleSelectModel} value={this.state.chosenModel || ''}>

                                  <option value='' disabled>Base model</option>

                                  {this.state.d_models.map(model => {

                                    return (<option value={model}>{model}</option>)


                                  })}
                          </select>
                          <br></br>


                          <input type="text" name="new_model" placeholder="New model"/>


                  </form>




                          <div id="trainButton" className="buttonDiv">
                            <Button className="btn" name="trainButton" variant="contained" color="primary" onClick={this.startTraining}>
                              {this.state.tbotOff ? "Start" : "Stop"}
                            </Button>
                          </div>




              </div>


                    )

            }
}
