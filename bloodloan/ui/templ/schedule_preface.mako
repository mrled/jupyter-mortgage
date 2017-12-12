<%page args="interestrate, principal, term, overpayment, appreciation, monthlypayments, monthlypayments_no_over" />

<%!
from bloodloan.mortgage.mmath import MONTHS_IN_YEAR
from bloodloan.ui.uiutil import dollar, percent
%>

<h2>Mortgage amortization schedule</h2>

<p>Amortization schedule for a <span>${dollar(principal)}</span> loan over ${term} months at ${percent(interestrate)} interest.</p>

<p>Expect the property to appreciate ${percent(appreciation)} each year.</p>

<%
term_over_months = len(monthlypayments)
term_over_years = int(term_over_months / MONTHS_IN_YEAR)

term_noover_months = len(monthlypayments_no_over)
term_noover_years = int(term_noover_months / MONTHS_IN_YEAR)

diff_months = len(monthlypayments_no_over) - len(monthlypayments)
diff_years = int(diff_months / MONTHS_IN_YEAR)

int_over = monthlypayments[-1].totalinterest
int_noover = monthlypayments_no_over[-1].totalinterest
int_diff = int_noover - int_over
%>

%if overpayment != 0:
    <p>
        With a monthy overpayment of ${dollar(overpayment)},
        you can expect to pay off the loan in ${term_over_years} years (${term_over_months} months),
        or ${diff_years} years (${diff_months} months)
        faster than the initial ${term_noover_years} year (${term_noover_months} month) term.
    </p>
    <p>
        This means you will pay <span>${dollar(int_over)}</span> in interest over the term of the loan,
        saving <span>${dollar(int_diff)}</span>
        of the full <span>${dollar(int_noover)}</span>
        that would be paid over the entire term of the loan without an overpayment.
    </p>
%else:
    <p>
        With a montly overpayment of ${dollar(0)},
        you will pay off the loan in ${term_over_years} years (${term_over_months} months).
        This will result in total interest payment of <span>${dollar(int_over)}</span>.
    </p>
%endif
