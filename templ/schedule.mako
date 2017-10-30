<%page args="apryearly, principal, term, overpayment, appreciation, loanpayments, yearly" />
<%
from mortgageui import dollar
%>

<h1>Mortgage amortization schedule</h1>

<!--Not sure why I need the <span> here, but if I do not include it Jupyter does something really fucked up to my text-->
<p>Amortization schedule for a <span>${dollar(principal)}</span> loan over ${term} months at ${apryearly}% interest, including a ${dollar(overpayment)} overpayment each month. Expect the property to appreciate ${appreciation}% each year.
</p>

<table>

<tr>
    %if yearly:
        <th>Year</th>
    %else:
        <th>Month</th>
    %endif
    <th>Regular payment</th>
    <th>Interest</th>
    <th>Balance</th>
    <th>Overpayment</th>
    <th>Remaining principal</th>
    <th>Value</th>
    <th>Equity</th>
</tr>

<tr>
    <td>Initial loan amount</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>${dollar(principal)}</td>
    <td>${dollar(principal)}</td>
    <td>${dollar(0)}</td>
</tr>

%for payment in loanpayments:
    <tr>
        <td>${payment.index}</td>
        <td>${dollar(payment.totalpmt)}</td>
        <td>${dollar(payment.interestpmt)}</td>
        <td>${dollar(payment.balancepmt)}</td>
        <td>${dollar(payment.overpmt)}</td>
        <td>${dollar(payment.principal)}</td>
        <td>${dollar(payment.value)}</td>
        <td>${dollar(payment.equity)}</td>
    </tr>
%endfor

</table>
