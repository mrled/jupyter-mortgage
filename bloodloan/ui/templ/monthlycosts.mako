<%page args="firstmonth" />

<%!
from bloodloan.ui.ui import dollar
%>

<h3>Monthly cost breakdown</h3>

<p>
    Note:
    the "First month value" column (and the combined total at the bottom)
    is calculated from the very first month of the loan;
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
    <th>First month value</th>
</tr>

%for cost in firstmonth.othercosts:
    <tr>
        <td>${cost.label}</td>
        <td>${cost.calcstr}</td>
        <td>${dollar(cost.value)}</td>
    </tr>
%endfor
<tr>
    <th>Total costs</th>
    <th></th>
    <th>${dollar(sum([c.value for c in firstmonth.othercosts]))}</th>
</tr>

</table>
