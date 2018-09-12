import React, { Component } from "react"
import axios from "axios";
import Select from 'react-select';



var x = window.location.href.split("/");
let WEBSITEHOST = x[0] + "//" + x[2];

export default class PatientInfo extends Component {

  constructor(props) {
        super(props);



        // in the constructor, get the names of all patients and fill up a list
        this.state = { pnames: [], selectedPatient: null, conversationData: [], selfHarmConversations: [], selectedConversation: null, selectedSelfHarmConversation: null};

        this.handleSelectPatient = this.handleSelectPatient.bind(this);
        this.handleSelectCID = this.handleSelectCID.bind(this);
    }

    // add functions to then use axios to query flask route for info about those patients
    // in those flask functions, return jsonify() with the html tables filled in
    // Make it nice using the data tables javascript plugin.

    componentDidMount() {


      fetch(`${WEBSITEHOST}/getnames`).then((response) => {
          response.json().then((data) => {
              var pnames = [];
              data.forEach(function(el){ pnames.push(el['userName'])});
              this.setState({pnames: pnames});
          });
      });

    }

    // handleSelectPatient(event) {
    //   event.preventDefault();
    //   this.setState({selectedPatient: event.target.value});
    //
    //   if (event.target.value == null || event.target.value == '') {
    //     this.setState({selectedPatient: null, selectedConversation: null});
    //   } else {
    //
    //     var toSend = new FormData();
    //     toSend.set('userName', event.target.value);
    //
    //
    //     axios({
    //       method: 'post',
    //       url: `${WEBSITEHOST}/getdetails`,
    //       data: toSend
    //     }).then((response) => {
    //       console.log(response.data);
    //       this.setState({conversationData: response.data["conversations"], selfHarmConversations: response.data["selfHarmConversations"]});
    //     });
    //   }

    handleSelectPatient = (selectedOption) => {

      var selectedValue = selectedOption.value;
      console.log(selectedValue);
      console.log(selectedValue == 'None');

      this.setState({selectedPatient: selectedOption});

      if (selectedValue == null || selectedValue == 'None') {
        this.setState({selectedConversation: null, selectedSelfHarmConversation: null, conversationData: [], selfHarmConversations: []});
        console.log("HELLO!");
      } else {

        var toSend = new FormData();
        toSend.set('userName', selectedValue);


        axios({
          method: 'post',
          url: `${WEBSITEHOST}/getdetails`,
          data: toSend
        }).then((response) => {
          console.log(response.data);
          this.setState({conversationData: response.data["conversations"], selfHarmConversations: response.data["selfHarmConversations"]});
        });
      }



    };

    handleSelectCID = (selectedOption) => {
      var selectedValue = selectedOption.value;

      this.setState({selectedConversation: selectedOption});

    };

    handleSelectSelfHarmCID = (selectedOption) => {
      var selectedValue = selectedOption.value;

      this.setState({selectedSelfHarmConversation: selectedOption});

    };





    render(){


          // var
          // className= {"cidOption " + }

          var divisionByZeroWarning = this.state.conversationData.length == 0;

          const patientNames = [

            { value: 'None', label: '' },
            ...this.state.pnames.map(pname => {
                    return ({value: pname, label: pname})
            })

          ];

          const convs = [

            { value: 'None', label: '' },
            ...this.state.conversationData.map((conversation, index) => {

                    return ({value: Number(index), label: (index + 1)});
            })
          ];

          const selfHarmConvs = [

            { value: 'None', label: '' },
            ...this.state.selfHarmConversations.map((conversation, index) => {

                    return ({value: Number(index), label: (index + 1)});
            })
          ];






          return (


            <div>

                    <div id="pNamePanel" className="infoPanel">


                        <h2>Select a patient</h2>



                        <Select
                          className="customSelect PatientSelect"
                          value= {this.state.selectedPatient || { value: 'None', label: '' }}
                          onChange={this.handleSelectPatient}
                          options={patientNames}
                        ></Select>

                        <table id="statsTable">

                        <thead>
                              <tr scope="row">
                                  <th scope="col">
                                      Number of conversations
                                  </th>
                                  <th scope="col">
                                      Percentage involving self harm
                                  </th>
                              </tr>
                        </thead>




                          <tbody>

                                {divisionByZeroWarning ?

                                  <tr scope="row">  <td><br></br></td>   <td><br></br></td>  </tr>

                                  :

                                  <tr scope="row">
                                    <td>{this.state.conversationData.length + this.state.selfHarmConversations.length}</td>
                                    <td>{String(parseFloat((this.state.selfHarmConversations.length / (this.state.selfHarmConversations.length + this.state.conversationData.length)) * 100).toFixed(3)) + "%"}</td>
                                  </tr>

                                }

                          </tbody>



                        </table>

                    </div>


                    <div className="infoPanel">

                            <h2>Conversations mentioning self harm</h2>

                            <Select
                              className="customSelect cidSelect"
                              value= {this.state.selectedSelfHarmConversation || { value: 'None', label: '' }}
                              onChange={this.handleSelectSelfHarmCID}
                              options={selfHarmConvs}
                            ></Select>

                            <table id="selfHarmTable">
                                    <thead>
                                          <tr scope="row">
                                              <th scope="col">
                                                  Speaker
                                              </th>
                                              <th scope="col">
                                                  Message
                                              </th>
                                          </tr>
                                    </thead>



                                                {this.state.selectedSelfHarmConversation && this.state.selectedSelfHarmConversation.value != 'None' ?


                                                  <tbody>
                                                {this.state.selfHarmConversations[this.state.selectedSelfHarmConversation.value]['utterances'].map(message => {
                                                        return (

                                                          <tr scope="row">

                                                        <td className="userName">{message.username == "bot" ? message.username : this.state.selectedPatient.value}</td>
                                                        <td className="messageContent">{message.message.text}</td>

                                                        </tr>

                                                        )
                                                })}

                                                </tbody>




                                                  :
                                                  <tbody><tr scope="row">  <td><br></br></td>   <td><br></br></td> </tr></tbody>
                                                }





                            </table>
                      </div>


                    <div className="infoPanel">

                          <h2>Other Conversations</h2>

                            <Select
                              className="customSelect cidSelect"
                              value= {this.state.selectedConversation || { value: 'None', label: '' }}
                              onChange={this.handleSelectCID}
                              options={convs}
                            ></Select>

                            <table id="conversationTable">
                                    <thead>
                                          <tr scope="row">
                                              <th scope="col">
                                                  Speaker
                                              </th>
                                              <th scope="col">
                                                  Message
                                              </th>
                                          </tr>
                                    </thead>



                                                {this.state.selectedConversation && this.state.selectedConversation.value != 'None' ?


                                                  <tbody>
                                                {this.state.conversationData[this.state.selectedConversation.value]['utterances'].map(message => {
                                                        return (

                                                          <tr scope="row">

                                                        <td className="userName">{message.username == "bot" ? message.username : this.state.selectedPatient.value}</td>
                                                        <td className="messageContent">{message.message.text}</td>

                                                        </tr>

                                                        )
                                                })}

                                                </tbody>




                                                  :
                                                  <tbody><tr scope="row"> <td><br></br></td>   <td><br></br></td>  </tr></tbody>
                                                }





                            </table>
                      </div>





            </div>


          )

    }


}
