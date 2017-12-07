<%page args="costs, rent, mortgagepmt" />

<%!
from bloodloan.ui.ui import dollar
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

%for cost in costs:
    <tr>
        <td>${cost.label}</td>
        <td>${cost.calcstr}</td>
        <td></td>
        <td>${dollar(cost.value)}</td>
    </tr>
%endfor

<%
total_costs = sum([c.value for c in costs])
cashflow = rent - mortgagepmt - total_costs
%>

<tr>
    <th colspan="2">Cashflow</th>
    <th colspan="2">${dollar(cashflow)}</th>
</tr>

</table>
