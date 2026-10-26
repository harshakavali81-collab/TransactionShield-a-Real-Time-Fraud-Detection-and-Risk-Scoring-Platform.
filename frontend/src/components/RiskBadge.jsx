import React from 'react';
export default function RiskBadge({risk}) {return <span className={'risk-tag '+String(risk||'LOW').toLowerCase()}><span className="risk-dot"/>{risk||'LOW'}</span>}
