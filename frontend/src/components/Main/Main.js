import React, { useState, useEffect, Fragment } from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import Snackbar from '@material-ui/core/Snackbar';
import webSocket from 'socket.io-client';

import classes from './Main.module.css';

const Main = () => {
    const [ws,setWs] = useState(null)
    const [ip, setIp] = useState('')
    const [echo, setEcho] = useState('')
    const [serverResp, setServerResp] = useState('')
    const [state, setState] = useState({
        open: false,
        vertical: 'top',
        horizontal: 'center',
      });
    
    const { vertical, horizontal, open } = state;

    const handleClose = () => {
        setState({ ...state, open: false });
    };

    const changeIPHandle = (e) => {
        setIp(e.target.value)
    }

    const changeEchoTextHandle = (e) => {
        setEcho(e.target.value)
    }

    const connectWebSocket = () => {
        //開啟
        setWs(webSocket(`http://${ip}:8080`))
    }

    useEffect(()=>{
        if(ws){
            //連線成功在 console 中打印訊息
            console.log('success connect!')
            setState({ open: true, ...state });
            //設定監聽
            initWebSocket()
        }
    },[ws])

    useEffect(()=>{
        if(ws){
            ws.emit('client_event', echo)
        }
    },[echo])

    const initWebSocket = () => {
        //對 getMessage 設定監聽，如果 server 有透過 getMessage 傳送訊息，將會在此被捕捉
        ws.on('server_response', message => {
            setServerResp(message)
        })
    }

    return(
        <div>
        <div className={classes.MainContent}>
            <div>
                <TextField id="connection-ip" label="Server IP" defaultValue={'192.168.50.18'} onChange={changeIPHandle} />
                <Button variant="contained" color="primary" onClick={connectWebSocket}>Connect</Button>
            </div>
            <div>
                <TextField id="echo-test" defaultValue={'echo test'} onChange={changeEchoTextHandle} />
            </div>
            <Paper elevation={3}>
                    {serverResp}
                </Paper>
        </div>
        <Snackbar
            anchorOrigin={{ vertical, horizontal }}
            open={open}
            onClose={handleClose}
            message="success connect!"
            key={vertical + horizontal}
        />
        </div>
    )
}

export default Main;