(this.webpackJsonpfrontend=this.webpackJsonpfrontend||[]).push([[0],{105:function(e,t){},111:function(e,t,n){"use strict";n.r(t);var a=n(0),c=n.n(a),o=n(7),r=n.n(o),i=(n(77),n(78),n(62)),l=n.n(i),u=function(){return c.a.createElement("div",{className:l.a.HeaderBar},c.a.createElement("div",null,"DigiWeb"))},s=n(38),m=n(26),f=n(147),d=n(146),v=n(145),p=n(149),b=n(63),h=n.n(b),E=n(64),O=n.n(E),j=function(){var e=Object(a.useState)(null),t=Object(m.a)(e,2),n=t[0],o=t[1],r=Object(a.useState)(""),i=Object(m.a)(r,2),l=i[0],u=i[1],b=Object(a.useState)(""),E=Object(m.a)(b,2),j=E[0],g=E[1],w=Object(a.useState)(""),C=Object(m.a)(w,2),_=C[0],S=C[1],k=Object(a.useState)({open:!1,vertical:"top",horizontal:"center"}),y=Object(m.a)(k,2),B=y[0],M=y[1],H=B.vertical,x=B.horizontal,z=B.open;Object(a.useEffect)((function(){n&&(console.log("success connect!"),M(Object(s.a)({open:!0},B)),N())}),[n]),Object(a.useEffect)((function(){n&&n.emit("client_event",j)}),[j]);var N=function(){n.on("server_response",(function(e){S(e)}))};return c.a.createElement("div",null,c.a.createElement("div",{className:O.a.MainContent},c.a.createElement("div",null,c.a.createElement(d.a,{id:"connection-ip",label:"Server IP",defaultValue:"192.168.50.18",onChange:function(e){u(e.target.value)}}),c.a.createElement(f.a,{variant:"contained",color:"primary",onClick:function(){o(h()("http://".concat(l,":8080")))}},"Connect")),c.a.createElement("div",null,c.a.createElement(d.a,{id:"echo-test",defaultValue:"echo test",onChange:function(e){g(e.target.value)}})),c.a.createElement(v.a,{elevation:3},_)),c.a.createElement(p.a,{anchorOrigin:{vertical:H,horizontal:x},open:z,onClose:function(){M(Object(s.a)(Object(s.a)({},B),{},{open:!1}))},message:"success connect!",key:H+x}))};var g=function(){return c.a.createElement("div",{className:"App"},c.a.createElement(u,null),c.a.createElement(j,null))};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));r.a.render(c.a.createElement(c.a.StrictMode,null,c.a.createElement(g,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))},62:function(e,t,n){e.exports={HeaderBar:"Header_HeaderBar__1Udn1"}},64:function(e,t,n){e.exports={MainContent:"Main_MainContent__2y5aU"}},72:function(e,t,n){e.exports=n(111)},77:function(e,t,n){},78:function(e,t,n){}},[[72,1,2]]]);
//# sourceMappingURL=main.5d8d8a62.chunk.js.map