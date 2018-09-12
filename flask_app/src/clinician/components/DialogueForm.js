import React, { Component } from "react";
import axios from "axios";

// https://stackoverflow.com/questions/36512686/react-dynamically-add-input-fields-to-form

var x = window.location.href.split("/");
let WEBSITEHOST = x[0] + "//" + x[2];

const DEFAULT_DIALOGUE_FILE = "defaultDialogues.txt";


class SimpleNode extends Component {
    constructor(props) {
      super(props);
    }

    render() {
      return (

        <div>

        {this.props.input.lbl == '0' ?
            (
              <div className="SimpleNode node">
              <div className="vrow">
              <p> {this.props.input.lbl} </p> <textarea type="text" key={this.props.input.lbl} name={this.props.input.lbl}></textarea>
              </div>
              </div>
        ) :
            (
        <div>
        <div className="line1"></div>
          <div className="SimpleNode node">
            <div className="vrow">
            <p> {this.props.input.lbl} </p> <textarea type="text" key={this.props.input.lbl} name={this.props.input.lbl}></textarea>
            </div>
          </div>
        </div> )}

        </div>
      )
    }
}





class ValidateNode extends Component {
    constructor(props) {
      super(props);
    }

    render() {
      return (
        <div>
        <div className="line1"></div>
            <div className="ValidateNode node"> {this.props.input.lbl}

              <div className="acceptedInputs vrow">
                  <p> Accepted inputs: </p>
                  <input type="text" key={this.props.input.lbl + "/a"} name={this.props.input.lbl + "/a"}/>
              </div>
              <div className="successResponse vrow">
                  <p> Response on success: </p>
                  <textarea type="text" key={this.props.input.lbl + "/b"} name={this.props.input.lbl + "/b"}></textarea>
              </div>
        </div>
        </div>
      )
    }
}



class TreeNode extends Component {

  constructor(props) {
        super(props);
        this.parentInputLbl = props.input['lbl']
        var intents = window.setupData.intents
        this.state = { branches: [{'lbl':'default'}], intents: intents || [], intentChosen: null };

        this.appendBranch = this.appendBranch.bind(this);
        this.removeBranch = this.removeBranch.bind(this);
        this.handleSelect = this.handleSelect.bind(this);
    }

  // componentDidMount() {
  //
  //
  //   fetch(`${WEBSITEHOST}/get_intents`).then((response) => {
  //       response.json().then((data) => {
  //           var intents = [];
  //           var intents = data;
  //           // data.forEach(function(el){ intents.push(el['userName'])});
  //           this.setState({intents: intents});
  //       });
  //   });
  //
  // }

  appendBranch(e) {
        e.preventDefault();

        if (this.state.intentChosen == "" || !this.state.intentChosen) {
          alert("You must choose an intent");
        } else{
          var newBranch = {'lbl': this.state.intentChosen};
          this.setState({ branches: [...this.state.branches, newBranch] });
        }

    }

  removeBranch(e) {
        e.preventDefault();
        var ar = [...this.state.branches];
        ar.pop();

        if (ar.length > 0) {
            this.setState({ branches: ar });
        }

    }

  handleSelect(event) {
    event.preventDefault();
    this.setState({intentChosen: event.target.value})

  }

    render() {
      return (
        <div>
        <div className="line1"></div>
        <div className="TreeNode node">

                {this.state.branches.map(branch => <Branch lbl= {this.parentInputLbl + ':' + branch['lbl']} intent = {branch['lbl']}/>)

                }

                <div className="selectIntents">
                  <select onChange={this.handleSelect} value={this.state.intentChosen || ''}>
                   <option value=''>Choose branch</option>
                   {this.state.intents.map(intent =>
                     <option value= {intent}>{intent}</option>
                   )}
                  </select>

                  <button onClick={this.appendBranch}>
                    +
                  </button>

                  <button onClick={this.removeBranch}>
                      -
                  </button>
                </div>

        </div>
        </div>
      )
    }
}

class Branch extends Component {

      constructor(props) {
            super(props);
            this.parentInputLbl = props.lbl
            this.intent = props.intent
            this.state = { inputs: [{'lbl': this.parentInputLbl + ',0', 'nodetype':'simple'}], nodeType: null };

            this.appendInput = this.appendInput.bind(this);
            this.removeInput = this.removeInput.bind(this);
            this.handleSelect = this.handleSelect.bind(this);
        }


        appendInput(e) {
              e.preventDefault();


              if (!(this.state.nodeType)) {
                alert("Select a valid node type")
              } else {
                var nt = this.state.nodeType;
                var newInput = {'lbl': this.parentInputLbl + `,${this.state.inputs.length}`, 'nodetype': nt};
                this.setState({ inputs: [...this.state.inputs, newInput] });
              }
          }

        removeInput(e) {
              e.preventDefault();
              var ar = [...this.state.inputs];
              ar.pop();

              if (ar.length > 0) {
                  this.setState({ inputs: ar });
              }

          }

        handleSelect(event) {
          event.preventDefault();
          this.setState({nodeType: event.target.value})

        }

        render() {
            return ( <div className="branch node">

            <h2> {this.intent} </h2>

            {this.state.inputs.map(input => {

                        if(input.nodetype == 'simple')
                            return <SimpleNode input={input}/>
                        else if(input.nodetype == 'validate')
                            return <ValidateNode input={input}/>
                        else if(input.nodetype == 'tree')
                            return <TreeNode input={input}/>
                        })

            }

            <div className="selectNode">
              <select onChange={this.handleSelect} value={this.state.nodeType || ''}>
                  <option value="">Choose Node</option>
                  <option value="simple">Standard</option>
                  <option value="validate">Validate input</option>
                  <option value="tree">Branch on intent</option>
              </select>
              <button onClick={this.appendInput}>
                +
              </button>

              <button onClick={this.removeInput}>
                  -
              </button>
            </div>

          </div> )
        }

}


export default class DialogueForm extends Component {

  constructor(props) {
        super(props);

        this.state = { inputs: [{'lbl':'0', 'nodetype':'simple'}], nodeType: null, dialogue_files: this.props.dialogue_files || null, FileToDelete: null, selectedDType: 'Questionnaire'};

        this.appendInput = this.appendInput.bind(this);
        this.removeInput = this.removeInput.bind(this);
        this.handleSelect = this.handleSelect.bind(this);
        this.handleSelectFile = this.handleSelectFile.bind(this);
        this.handleSelectFileToDelete = this.handleSelectFileToDelete.bind(this);
        this.handleSelectDType = this.handleSelectDType.bind(this);
    }

  componentWillReceiveProps(nextProps){
    this.setState({dialogue_files: nextProps.dialogue_files})
  }

  appendInput(e) {
        e.preventDefault();

        if (!(this.state.nodeType) || this.state.nodeType == '') {
          alert("Select a valid node type")
        } else {
          var nt = this.state.nodeType;
          var newInput = {'lbl': `${this.state.inputs.length}`, 'nodetype': nt};
          this.setState({ inputs: [...this.state.inputs, newInput] });
        }
    }

  removeInput(e) {
        e.preventDefault();
        var ar = [...this.state.inputs];
        ar.pop();

        if (ar.length > 0) {
            this.setState({ inputs: ar });
        }

    }

  handleSelect(event) {
    event.preventDefault();
    this.setState({nodeType: event.target.value})

  }

  handleSelectFile(event) {
    event.preventDefault();
    this.setState({selectedFile: event.target.value})
  }

  handleSelectFileToDelete(event) {
    event.preventDefault();
    this.setState({FileToDelete: event.target.value})
  }

  handleSelectDType(event) {
    event.preventDefault()
    this.setState({selectedDType: event.target.value})
  }

  onSubmit = (e) => {
    e.preventDefault();

    var formData = new FormData(document.getElementById("dForm"));

    // console.log(e);
    //
    // for (var value of formData.values()) {
    //    console.log(value);
    // }

    var new_file = formData.get("NewFile");
    var dName = formData.get("DialogueName");
    var parts = new_file.split('.')

    if (new_file == DEFAULT_DIALOGUE_FILE) {
      alert("Cannot overwrite the default dialogues file");
    } else if (parts.length > 2 || parts.length < 2) {
      alert("Invalid file name");
    } else if (parts.pop() != 'txt') {
      alert("File must end in .txt");
    } else if (!dName) {
      alert("Dialogue must be named");
    } else {
      axios({
        method: 'post',
        url: `${WEBSITEHOST}/addDialogue`,
        data: formData
      }).then((response) => {
        alert(response.data);
        if (response.data == "Dialogue Saved!") {
          let array = this.state.dialogue_files;
          if (array.includes(new_file)) {
          } else {
            array.push(new_file);
          }
          this.props.setDialogueFiles(array);
        }

      });

    }

  }

  deleteDialogueFile = (e) => {
    e.preventDefault();

    if (this.state.FileToDelete == null || this.state.FileToDelete == '') {
      alert("Choose a file to delete");
    } else {
      let formData = new FormData();
      formData.append('dfile', this.state.FileToDelete);

      axios({
        method: 'post',
        url: `${WEBSITEHOST}/deleteDialogue`,
        data: formData
      }).then((response) => {

        alert(response.data);

        let array = this.state.dialogue_files;
        let index = array.indexOf(this.state.FileToDelete);
        if (index > -1) {
          array.splice(index, 1);
        }

        this.setState({FileToDelete: null});
        this.props.setDialogueFiles(array);
      });
    }

  }

  render(){
        return (
            <div className="dialogueForm">


                <h2> Delete dialogue file </h2>

                <form id="deleteDialogueFilesForm" onSubmit={this.deleteDialogueFile}>
                    <div className="dFormOptions">
                          <p>Base file: </p>
                          <select onChange={this.handleSelectFileToDelete} value={this.state.FileToDelete || ''}>

                            <option value=''></option>

                            {this.state.dialogue_files.filter(function(dfile) {
                              if (dfile == DEFAULT_DIALOGUE_FILE) {
                                return false;
                              } else {
                                return true;
                              }
                            }).map(dfile => {
                              return (<option value={dfile}>{dfile}</option>)
                            })}
                          </select>
                    </div>
                    <input className="submitForm" type="submit" value="Delete Dialogue"/>

                </form>



                <h2> Create new dialogues </h2>

                <form id="dForm" onSubmit={this.onSubmit}>

                <div className="dFormOptions">

                  <p>Base file: </p>
                  <select onChange={this.handleSelectFile} value={this.state.selectedFile || ''}>

                    <option value=''></option>

                    {this.state.dialogue_files.map(dfile => {

                      return (<option value={dfile}>{dfile}</option>)


                    })}
                  </select>
                  <input id="BaseFile" type="text" name="BaseFile" value={this.state.selectedFile || ''}/> <br></br>

                  <p>New file: </p><input id="NewFile" type="text" name="NewFile"/> <br></br>


                <div id="dnameDiv">
                  <p>Dialogue Name: </p><input id="DialogueName" type="text" name="DialogueName"/> <br></br>
                </div>

                <div id="dtypeDiv">


                  <p>Dialogue Type: </p>
                  <select onChange={this.handleSelectDType} value={this.state.selectedDType}>
                    <option value='Questionnaire'>Questionnaire</option>
                    <option value='RDialogue'>Resilience dialogue</option>
                  </select>
                  <input className="hideThis" id="DialogueType" type="text" name="DialogueType" value={this.state.selectedDType}/> <br></br>
                </div>

                </div>

                <div className="tree">
                    {this.state.inputs.map(input => {

                                if(input.nodetype == 'simple')
                                    return <SimpleNode input={input}/>
                                else if(input.nodetype == 'validate')
                                    return <ValidateNode input={input}/>
                                else if(input.nodetype == 'tree')
                                    return <TreeNode input={input}/>
                                })



                    }

                </div>





                <div className="selectNode">

                  <select onChange={this.handleSelect} value={this.state.nodeType || ''}>
                      <option value="">Choose Node</option>
                      <option value="simple">Standard</option>
                      <option value="validate">Validate input</option>
                      <option value="tree">Branch on intent</option>
                  </select>
                  <button onClick={this.appendInput}>
                    +
                  </button>

                  <button onClick={this.removeInput}>
                      -
                  </button>
                </div>

                <br/>

                <input className="submitForm" type="submit" value="Save Dialogue"/>
            </form>

            </div>
        );
    }



}
