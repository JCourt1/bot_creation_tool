import React, { Component } from "react"
import axios from "axios";
import Button from '@material-ui/core/Button';

var x = window.location.href.split("/");
let WEBSITEHOST = x[0] + "//" + x[2];

export default class ControlRoom extends Component {

  constructor(props) {
        super(props);

        this.state = { chosenModel: null, selectedFile: null, d_models: this.props.d_models, d_files: this.props.dialogue_files, botOff: null};
        this.handleSelectModel = this.handleSelectModel.bind(this);
        this.handleSelectFile = this.handleSelectFile.bind(this);
        this.startBot = this.startBot.bind(this);

    }

    componentDidMount(){

      fetch(`${WEBSITEHOST}/checkpbotoff`).then((response) => {
            response.json().then((data) => {
              this.setState({botOff: data});
              console.log(this.state.botOff);
        });
      });

    }

    componentWillReceiveProps(nextProps){
      this.setState({d_models: nextProps.d_models, d_files: nextProps.dialogue_files});
    }

    handleSelectModel(event) {
      event.preventDefault();
      this.setState({chosenModel: event.target.value})

    }

    handleSelectFile(event) {
      event.preventDefault();
      this.setState({selectedFile: event.target.value})
    }

    startBot = () => {

      var formData = new FormData(document.getElementById("runBotForm"));

      var pbot_base_model = formData.get("pbot_base_model");
      var dfile = formData.get("dfile");
      var bad_values = ['', 'None', undefined, null];

      console.log(pbot_base_model);
      console.log(dfile);

      if ((bad_values.includes(pbot_base_model) || bad_values.includes(dfile)) && this.state.botOff) {
        alert("Choose settings before launching bot.");
      } else {
        axios({
          method: 'post',
          url: `${WEBSITEHOST}/toggle`,
          data: formData
        }).then((response) => {
          if (response.data == "success") {
            this.setState({botOff: !this.state.botOff});
            this.props.OnOffSwitch("TBot");
          } else {
            alert("Something went wrong.");
          }

        });
      }

    }


    render(){

          if (this.props.OnOffFlag) {
            this.setState({botOff: true});
            this.props.OnOffSwitch("reset");
          }

          return (

            <div id="runBotContainer">

              <h2>Configure and Launch</h2>

              <div id="formContainer">

                    <form method="post" id="runBotForm">

                            <select id="model" onChange={this.handleSelectModel} value={this.state.chosenModel || ''}>

                                    <option value='' disabled>Model to run</option>

                                    {this.state.d_models.map(model => {

                                      return (<option value={model}>{model}</option>)


                                    })}
                            </select>
                            <input className="Hidden" type="text" name="pbot_base_model" value={this.state.chosenModel || ''}/>

                            <select id="dFileInput" onChange={this.handleSelectFile} value={this.state.selectedFile || ''}>

                              <option value='' disabled>Dialogues file</option>

                              {this.state.d_files.map(dfile => {

                                return (<option value={dfile}>{dfile}</option>)


                              })}
                            </select>
                            <input className="Hidden" id="dfile" type="text" name="dfile" value={this.state.selectedFile || ''}/> <br></br>
                    </form>
              </div>


              <div className="buttonDiv">
                <Button className= {"btn " + (this.state.botOff ? 'off' : 'pBotGlow')} name="runBotButton" variant="contained" color="primary" onClick={this.startBot }>
                  {this.state.botOff ? "Switch Bot on" : "Switch Bot off"}
                </Button>
              </div>

            </div>


          )

    }


}
