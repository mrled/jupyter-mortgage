<%page args="closeresult" />

<%!
from bloodloan.ui.uiutil import dollar
%>

<h2>Closing</h2>

<p>Final loan amount and closing costs are listed here</p>

<h3>Principal</h3>
<table>
    <tr>
        <th>Description</th>
        <th>Amount</th>
    </tr>
    %for cost in closeresult.principal:
        <tr>
            <td>${cost.label}</td>
            <td><span>${dollar(cost.value)}</span></td>
        </tr>
    %endfor
    %if len(closeresult.principal) > 1:
        <tr>
            <th>Total</th>
            <th><span>${dollar(closeresult.principal_total)}</span></th>
        </tr>
    %endif
</table>

<h3>Cash required at closing</h3>
<table>
    <tr>
        <th>Description</th>
        <th>Calculation</th>
        <th>Amount</th>
    </tr>
    %for cost in closeresult.downpayment + closeresult.fees:
        <tr>
            <td>${cost.label}</td>
            <td>${cost.calcstr}</td>
            <td><span>${dollar(cost.value)}</span></td>
        </tr>
    %endfor
    <!--
    %for cost in closeresult.fees:
        <tr>
            <th>${cost.label}</th>
            <td><span>${dollar(cost.value)}</span></td>
        </tr>
    %endfor
    -->
    <tr>
        <th colspan="2">Total</th>
        <th><span>${dollar(closeresult.downpayment_total + closeresult.fees_total)}</span></th>
    </tr>
</table>
