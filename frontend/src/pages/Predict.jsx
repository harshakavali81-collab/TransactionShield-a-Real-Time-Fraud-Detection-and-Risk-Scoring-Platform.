import React from 'react';
import TransactionForm from '../components/TransactionForm';
export default function Predict({refresh}){return <><div className="page-title"><div><div className="eyebrow">TRANSACTION REVIEW</div><h1>Fraud Risk <span>Scoring</span></h1><p>Submit a demonstration transaction for risk scoring. Offline preview uses fictional rule simulation only.</p></div></div><TransactionForm onSuccess={refresh}/></>}
