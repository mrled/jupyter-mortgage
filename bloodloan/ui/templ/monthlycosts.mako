<%page args="costs, capexcosts, rent, mortgagepmt" />

<%!
from bloodloan.ui.uiutil import dollar
%>

<%
total_capex = sum([c.value for c in capexcosts])
total_othercosts = sum([c.value for c in costs])
cashflow = rent - mortgagepmt - total_capex - total_othercosts
%>

<h3>Monthly balance sheet</h3>

<p>
    Note:
    values displayed here are calculated from the very first month of the loan;
    over time, some values based on e.g. remaining principal
    will decrease.
</p>
<p>
    This decrease will be noted in the "other costs" column
    of the mortgage schedule,
    but is not detailed here.
</p>

<table>

<tr>
    <th>Description</th>
    <th>Calculation</th>
    <th>Credit</th>
    <th>Debit</th>
</tr>

<tr>
    <td>Mortgage payment</td>
    <td>constant amount</td>
    <td></td>
    <td>${dollar(mortgagepmt)}</td>
</tr>
<tr>
    <td>Projected monthly rent</td>
    <td>constant amount</td>
    <td>${dollar(rent)}</td>
    <td></td>
</tr>
<tr><td colspan="4"> </td></td>

%for cost in capexcosts:
    <tr>
        <td>${cost.label}</td>
        <td>${cost.calcstr}</td>
        <td></td>
        <td>${dollar(cost.value)}</td>
    </tr>
%endfor
<tr>
    <th colspan="2">CapEx total</th>
    <th colspan="2">${dollar(total_capex)}</th>
</tr>
<tr><td colspan="4"> </td></td>

%for cost in costs:
    <tr>
        <td>${cost.label}</td>
        <td>${cost.calcstr}</td>
        <td></td>
        <td>${dollar(cost.value)}</td>
    </tr>
%endfor
<tr>
    <th colspan="2">Other costs total</th>
    <th colspan="2">${dollar(total_othercosts)}</th>
</tr>
<tr><td colspan="4"> </td></td>

<tr>
    <th colspan="2">Cashflow</th>
    <th colspan="2">${dollar(cashflow)}</th>
</tr>

</table>
