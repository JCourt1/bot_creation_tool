
import classnames from "classnames";
import React from 'react';
import ReactDOM from 'react-dom';
import Button from '@material-ui/core/Button';
import axios from "axios";

var x = window.location.href.split("/");
let WEBSITEHOST = x[0] + "//" + x[2];

class Header extends React.Component {

      constructor() {
          super();

          this.onSubmit = this.onSubmit.bind(this);
      }

      onSubmit = (e) => {
        e.preventDefault();

        var formData = new FormData(document.getElementById("pChangeForm"));
        axios({
          method: 'post',
          url: `${WEBSITEHOST}/changePassword`,
          data: formData
        }).then((response) => {
          alert(response.data);
        });


      }

      render() {
          return (

              <div id="headerimg" className="description">
                <h1>
                 Mental Health Chat Bot
                </h1>

                <div id="passwordModal" class="modal">
                        <div class="modal-content">
                          <div class="modal-header">
                            <span onClick={() => {var m = document.getElementById("passwordModal"); m.style.display = "none"; m.style.zIndex = 0}} class="close">&times;</span>
                          </div>
                          <div class="modal-body">

                            <form id="pChangeForm" onSubmit={this.onSubmit}>

                                <p>Old password: </p> <input className="oldPW" type="password" name="oldPW" />
                                <p>New password: </p> <input className="newPW" type="password" name="newPW1" />
                                <p>Confirm new password: </p> <input className="newPW" type="password" name="newPW2" />

                                <div><input className="submitForm" type="submit" value="Change password"/></div>

                            </form>
                          </div>
                          <div class="modal-footer">
                          </div>
                        </div>
                </div>

                  <Button id="ChangePasswordBtn" name="logoutButton" variant="contained" color="primary" onClick={() => { var m = document.getElementById("passwordModal"); m.style.display = "block"; m.style.zIndex = 400 }}>
                    Change password
                  </Button>

                  <Button id="logoutButton" name="logoutButton" variant="contained" color="primary" onClick={() => { document.getElementById("logOutForm").submit(); }}>
                    Logout
                  </Button>



               </div>

          );
      }
  }


ReactDOM.render(<Header />, document.getElementById('header'));
