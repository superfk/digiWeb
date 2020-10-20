import React from 'react';
import BarcodeScannerComponent from "react-webcam-barcode-scanner";
 
const barcodeScanner = (props) => {
 
  return (
    <>
      <BarcodeScannerComponent
        width={500}
        height={500}
        onUpdate={(err, result) => {
          if (result) {
            props.updateResultHandler(result.text)
          }else
          {
            props.updateResultHandler('Not Found')
          }
        }}
      />
    </>
  )
}
 
export default barcodeScanner;