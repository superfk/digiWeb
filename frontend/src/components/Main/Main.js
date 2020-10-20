import React, { useState, useEffect } from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import BarcodeScanner from '../BarcodeScanner/BarcodeScanner';
import webSocket from 'socket.io-client';

import classes from './Main.module.css';

const PORT = 9031

const Main = () => {
    const [ws, setWs] = useState(null)
    const [ip, setIp] = useState('')
    const [echo, setEcho] = useState('')
    const [online, setOnline] = useState(false)
    const [batchName, setBatchName] = useState('')
    const [mearData, setMearData] = useState('measured data');
    const [datahistory, setDataHistory] = useState([])
    const [serverResp, setServerResp] = useState('')
    const [barcodeText, seBarcodeText] = useState('Not Found')
    const [state, setState] = useState({
        open: false,
        vertical: 'top',
        horizontal: 'center',
    });

    const changeIPHandle = (e) => {
        setIp(e.target.value)
    }

    const changeBatchNameHandler = (e) => {
        setBatchName(e.target.value)
    }

    const connectWebSocket = () => {
        //開啟
        setWs(webSocket(`https://${ip}:${PORT}`, {secure: true}))
    }

    const resetBatch = () => {
        ws.emit('init_batch', batchName)
    }
    const startMear = () => {
        ws.emit('mear')
    }
    const updateResultHandler =(text) => {
        seBarcodeText(text)
    }

    useEffect(() => {
        if (ws) {
            //連線成功在 console 中打印訊息
            console.log('success connect!')
            initWebSocket()
        }
    }, [ws])

    useEffect(() => {
        if (ws) {
            ws.emit('client_event', echo)
        }
    }, [echo])

    const initWebSocket = () => {
        //對 getMessage 設定監聽，如果 server 有透過 getMessage 傳送訊息，將會在此被捕捉
        ws.on('server_response', message => {
            setServerResp(message)
        })
        ws.on('server_sent_connect_ok', message => {
            if (message === 'Hi from Server') {
                setState({ open: true, ...state });
                setOnline(true)
            }
        })
        ws.on('send_mear_data', data => {
            setMearData(data)
        })
        ws.on('show_records', history => {
            setDataHistory(history)
        })
    }

    const connectionStatusClass = () => {
        if (online) {
            return [classes.ConnectLight, classes.Online]
        } else {
            return [classes.ConnectLight, classes.Offline]
        }
    }

    return (
        <div className={classes.MainContent}>
            <div>
                <TextField id="connection-ip" label="Server IP" defaultValue={'192.168.1.113'} size='small' onChange={changeIPHandle} />
                <Button variant="contained" onClick={connectWebSocket}>Connect</Button>
                <div className={connectionStatusClass().join(' ')}></div>
            </div>
            <div>
                <TextField id="batch-name" label="Batch Name" defaultValue={''} size='small' onChange={changeBatchNameHandler} />
                <Button variant="contained" onClick={resetBatch}>Reset Batch</Button>
            </div>
            <div style={{ width: '90%' }}>
                <Button variant="contained" fullWidth={true} onClick={startMear}>Measure</Button>
            </div>
            <div className={classes.Value}>
                <h1>{mearData}
                    <Divider />
                </h1>
            </div>
            <div className={classes.DataHistory}>
                <List component="nav" dense={true}>
                    {datahistory.map((elm,idx) => {
                        return <ListItem key={elm+idx}>
                            <ListItemText primary={elm} color='primary' />
                        </ListItem>
                    })}
                </List>
            </div>
            <div className={classes.Barcode}>
                <BarcodeScanner className={classes.Cam} updateResultHandler={updateResultHandler} />
                <div className={classes.BarcodeText}>{barcodeText}</div>
            </div>
        </div>
    )
}

export default Main;