import React from 'react';
import TransactionForm from '../components/TransactionForm';
export default function Predict({refresh}){return <><div className="page-title"><div><div className="eyebrow">TRANSACTION REVIEW</div><h1>Fraud Risk <span>Scoring</span></h1><p>Submit a demonstration transaction to the prediction API.</p></div></div><TransactionForm onSuccess={refresh}/></>}
