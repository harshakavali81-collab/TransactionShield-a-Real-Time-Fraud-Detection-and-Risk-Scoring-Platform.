import React from 'react';
export default function MetricCard({label,value,sub,icon:Icon,tone='blue'}) {return <section className="metric"><div className={'metric-icon '+tone}>{Icon && <Icon size={20}/>}</div><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-sub">{sub}</div></section>}
