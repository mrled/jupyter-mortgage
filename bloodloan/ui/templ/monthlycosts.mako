<%page args="firstmonth" />

<%!
from bloodloan.ui.ui import dollar
%>

<h3>Monthly cost breakdown</h3>

<table>

<tr>
    <th>Description</th>
    <th>Calculation</th>
    <th>Example (from first month)</th>
</tr>

%for cost in firstmonth.othercosts:
    <tr>
        <td>${cost.label}</td>
        <td>${cost.calcstr}</td>
        <td>${dollar(cost.value)}</td>
    </tr>
%endfor
<tr>
    <th>Total monthly costs (from first month)</th>
    <th></th>
    <th>${dollar(sum([c.value for c in firstmonth.othercosts]))}</th>
</tr>

</table>
