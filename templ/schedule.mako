<%page args="principal, value, loanpayments, paymentinterval_name" />

<%!
from mortgageui import dollar
%>

<table>

<tr>
    <th>${paymentinterval_name}</th>
    <th>Regular payment</th>
    <th>Total payment</th>
    <th>Interest</th>
    <th>Balance</th>
    <th>Overpayment</th>
    <th>Remaining principal</th>
    <th>Value</th>
    <th>Equity</th>
    <th>Total interest paid</th>
</tr>

<tr>
    <td>Initial loan amount</td>
    ## <td>${dollar(loanpayments[0].regularpmt)}</td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>${dollar(principal)}</td>
    <td>${dollar(value)}</td>
    <td>${dollar(0)}</td>
    <td>${dollar(0)}</td>
</tr>

%for payment in loanpayments:
    <tr>
        <td>${payment.index + 1}</td>
        <td>${dollar(payment.regularpmt)}</td>
        <td>${dollar(payment.totalpmt)}</td>
        <td>${dollar(payment.interestpmt)}</td>
        <td>${dollar(payment.balancepmt)}</td>
        <td>${dollar(payment.overpmt)}</td>
        <td>${dollar(payment.principal)}</td>
        <td>${dollar(payment.value)}</td>
        <td>${dollar(payment.equity)}</td>
        <td>${dollar(payment.totalinterest)}</td>
    </tr>
%endfor

</table>
