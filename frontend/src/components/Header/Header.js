import React from 'react';
import logo from '../../images/Bareiss_LOGO.png';

import classes from './Header.module.css';

const Header = () => {

    return(
        <div className={classes.HeaderBar}>
            <img className={classes.Logo} src={logo} alt="Background" />
            <div className={classes.Title} >DigiWeb</div>
        </div>
    )
}

export default Header;