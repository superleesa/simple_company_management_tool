function strftimeDateIntoYearMonth(date) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1; // Months are zero-indexed

  // Add leading zero if month is a single digit
  const formattedMonth = month < 10 ? `0${month}` : month;

  // Create the formatted string "year-month"
  return `${year}-${formattedMonth}`;
}

function generateThisMonthAndNMonthsAgoStrings(n){
  const currentDate = new Date();
  const currentMonthString = strftimeDateIntoYearMonth(currentDate);

  const nMonthsAgoDate = new Date(currentDate);
  nMonthsAgoDate.setMonth(currentDate.getMonth() - n);
  const nMonthAgoString = strftimeDateIntoYearMonth(nMonthsAgoDate);

  return [currentMonthString, nMonthAgoString];
}