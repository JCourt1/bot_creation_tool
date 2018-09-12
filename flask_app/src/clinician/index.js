// @flow
import "unfetch/polyfill";
import "babel-polyfill";
import classnames from "classnames";
import React from 'react';
import ReactDOM from 'react-dom';

import App from './trainApp';

ReactDOM.render(<App />, document.getElementById('everything'));
