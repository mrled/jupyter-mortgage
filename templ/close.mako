<%page args="closeresult" />

<%!
from mortgageui import dollar
%>

<h2>Closing</h2>

<p>Final loan amount and closing costs are listed here</p>

<h3>Loan breakdown</h3>
<table>
    %for cost in closeresult.principal:
        <tr><th>${cost.label}</th><td><span>${dollar(cost.value)}</span></td></tr>
    %endfor
    <tr><th>Total</th><th><span>${dollar(closeresult.principal_total)}</span></th></tr>
</table>

<h3>Down payment breakdown</h3>
<table>
    %for cost in closeresult.downpayment:
        <tr><th>${cost.label}</th><td><span>${dollar(cost.value)}</span></td></tr>
    %endfor
    <tr><th>Total</th><th><span>${dollar(closeresult.downpayment_total)}</span></th></tr>
</table>

<h3>Misc/other fees at closing</h3>
<table>
    %for cost in closeresult.fees:
        <tr><th>${cost.label}</th><td><span>${dollar(cost.value)}</span></td></tr>
    %endfor
    <tr><th>Total</th><th><span>${dollar(closeresult.fees_total)}</span></th></tr>
</table>
