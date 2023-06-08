        @Override
        public List<SavingsAccountData> extractData(final ResultSet rs) throws SQLException {

            List<SavingsAccountData> savingsAccountDataList = new ArrayList<>();
            HashMap<String, Long> savingsMap = new HashMap<>();
            String currencyCode = null;
            Integer currencyDigits = null;
            Integer inMultiplesOf = null;
            CurrencyData currency = null;
            HashMap<String, Long> transMap = new HashMap<>();
            HashMap<String, Long> taxDetails = new HashMap<>();
            HashMap<String, Long> chargeDetails = new HashMap<>();
            SavingsAccountTransactionData savingsAccountTransactionData = null;
            SavingsAccountData savingsAccountData = null;
            int count = 0;

            while (rs.next()) {
                final Long id = rs.getLong("id");
                final Long transactionId = rs.getLong("transactionId");
                final Long taxDetailId = JdbcSupport.getLongDefaultToNullIfZero(rs, "taxDetailsId");
                final Long taxComponentId = JdbcSupport.getLongDefaultToNullIfZero(rs, "taxComponentId");
                final String accountNo = rs.getString("accountNo");
                final Long chargeId = rs.getLong("chargeId");

                if (!savingsMap.containsValue(id)) {
                    if (count > 0) {
                        savingsAccountDataList.add(savingsAccountData);
                    }
                    count++;
                    savingsMap.put("id", id);

                    final String externalId = rs.getString("externalId");
                    final Integer depositTypeId = rs.getInt("depositType");
                    final EnumOptionData depositType = SavingsEnumerations.depositType(depositTypeId);
                    final Long groupId = JdbcSupport.getLong(rs, "groupId");
                    final Long groupOfficeId = JdbcSupport.getLong(rs, "groupOfficeId");
                    final GroupGeneralData groupGeneralData = new GroupGeneralData(groupId, groupOfficeId);

                    final Long clientId = JdbcSupport.getLong(rs, "clientId");
                    final Long clientOfficeId = JdbcSupport.getLong(rs, "clientOfficeId");
                    final ClientData clientData = ClientData.createClientForInterestPosting(clientId, clientOfficeId);

                    final Long glAccountIdForInterestOnSavings = rs.getLong("glAccountIdForInterestOnSavings");
                    final Long glAccountIdForSavingsControl = rs.getLong("glAccountIdForSavingsControl");

                    final Long productId = rs.getLong("productId");
                    final Integer accountType = rs.getInt("accountingType");
                    final AccountingRuleType accountingRuleType = AccountingRuleType.fromInt(accountType);
                    final EnumOptionData enumOptionDataForAccounting = new EnumOptionData(accountType.longValue(),
                            accountingRuleType.getCode(), accountingRuleType.getValue().toString());
                    final SavingsProductData savingsProductData = SavingsProductData.createForInterestPosting(productId,
                            enumOptionDataForAccounting);

                    final Integer statusEnum = JdbcSupport.getInteger(rs, "statusEnum");
                    final SavingsAccountStatusEnumData status = SavingsEnumerations.status(statusEnum);
                    final Integer subStatusEnum = JdbcSupport.getInteger(rs, "subStatusEnum");
                    final SavingsAccountSubStatusEnumData subStatus = SavingsEnumerations.subStatus(subStatusEnum);
                    final LocalDate lastActiveTransactionDate = JdbcSupport.getLocalDate(rs, "lastActiveTransactionDate");
                    final boolean isDormancyTrackingActive = rs.getBoolean("isDormancyTrackingActive");
                    final Integer numDaysToInactive = JdbcSupport.getInteger(rs, "daysToInactive");
                    final Integer numDaysToDormancy = JdbcSupport.getInteger(rs, "daysToDormancy");
                    final Integer numDaysToEscheat = JdbcSupport.getInteger(rs, "daysToEscheat");
                    Integer daysToInactive = null;
                    Integer daysToDormancy = null;
                    Integer daysToEscheat = null;

                    LocalDate localTenantDate = DateUtils.getBusinessLocalDate();
                    if (isDormancyTrackingActive && statusEnum.equals(SavingsAccountStatusType.ACTIVE.getValue())) {
                        if (subStatusEnum < SavingsAccountSubStatusEnum.ESCHEAT.getValue()) {
                            daysToEscheat = Math.toIntExact(
                                    ChronoUnit.DAYS.between(localTenantDate, lastActiveTransactionDate.plusDays(numDaysToEscheat)));
                        }
                        if (subStatusEnum < SavingsAccountSubStatusEnum.DORMANT.getValue()) {
                            daysToDormancy = Math.toIntExact(
                                    ChronoUnit.DAYS.between(localTenantDate, lastActiveTransactionDate.plusDays(numDaysToDormancy)));
                        }
                        if (subStatusEnum < SavingsAccountSubStatusEnum.INACTIVE.getValue()) {
                            daysToInactive = Math.toIntExact(
                                    ChronoUnit.DAYS.between(localTenantDate, lastActiveTransactionDate.plusDays(numDaysToInactive)));
                        }
                    }
                    final LocalDate approvedOnDate = JdbcSupport.getLocalDate(rs, "approvedOnDate");
                    final LocalDate withdrawnOnDate = JdbcSupport.getLocalDate(rs, "withdrawnOnDate");
                    final LocalDate submittedOnDate = JdbcSupport.getLocalDate(rs, "submittedOnDate");
                    final LocalDate activatedOnDate = JdbcSupport.getLocalDate(rs, "activatedOnDate");
                    final LocalDate closedOnDate = JdbcSupport.getLocalDate(rs, "closedOnDate");
                    final SavingsAccountApplicationTimelineData timeline = new SavingsAccountApplicationTimelineData(submittedOnDate, null,
                            null, null, null, null, null, null, withdrawnOnDate, null, null, null, approvedOnDate, null, null, null,
                            activatedOnDate, null, null, null, closedOnDate, null, null, null);

                    currencyCode = rs.getString("currencyCode");
                    currencyDigits = JdbcSupport.getInteger(rs, "currencyDigits");
                    inMultiplesOf = JdbcSupport.getInteger(rs, "inMultiplesOf");
                    currency = new CurrencyData(currencyCode, currencyDigits, inMultiplesOf);

                    final BigDecimal totalDeposits = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalDeposits");
                    final BigDecimal totalWithdrawals = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalWithdrawals");
                    final BigDecimal totalWithdrawalFees = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalWithdrawalFees");
                    final BigDecimal totalAnnualFees = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalAnnualFees");

                    final BigDecimal totalInterestEarned = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalInterestEarned");
                    final BigDecimal totalInterestPosted = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs, "totalInterestPosted");
                    final BigDecimal accountBalance = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs, "accountBalance");
                    final BigDecimal totalFeeCharge = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalFeeCharge");
                    final BigDecimal totalPenaltyCharge = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalPenaltyCharge");
                    final BigDecimal totalOverdraftInterestDerived = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs,
                            "totalOverdraftInterestDerived");
                    final BigDecimal totalWithholdTax = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "totalWithholdTax");
                    final LocalDate interestPostedTillDate = JdbcSupport.getLocalDate(rs, "interestPostedTillDate");

                    final BigDecimal minBalanceForInterestCalculation = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs,
                            "minBalanceForInterestCalculation");
                    final BigDecimal onHoldFunds = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "onHoldFunds");

                    final BigDecimal onHoldAmount = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "onHoldAmount");

                    BigDecimal availableBalance = accountBalance;
                    if (availableBalance != null && onHoldFunds != null) {

                        availableBalance = availableBalance.subtract(onHoldFunds);
                    }

                    if (availableBalance != null && onHoldAmount != null) {

                        availableBalance = availableBalance.subtract(onHoldAmount);
                    }

                    BigDecimal interestNotPosted = BigDecimal.ZERO;
                    LocalDate lastInterestCalculationDate = null;
                    if (totalInterestEarned != null) {
                        interestNotPosted = totalInterestEarned.subtract(totalInterestPosted).add(totalOverdraftInterestDerived);
                        lastInterestCalculationDate = JdbcSupport.getLocalDate(rs, "lastInterestCalculationDate");
                    }

                    final SavingsAccountSummaryData summary = new SavingsAccountSummaryData(currency, totalDeposits, totalWithdrawals,
                            totalWithdrawalFees, totalAnnualFees, totalInterestEarned, totalInterestPosted, accountBalance, totalFeeCharge,
                            totalPenaltyCharge, totalOverdraftInterestDerived, totalWithholdTax, interestNotPosted,
                            lastInterestCalculationDate, availableBalance, interestPostedTillDate);
                    summary.setPrevInterestPostedTillDate(interestPostedTillDate);

                    final boolean withHoldTax = rs.getBoolean("withHoldTax");
                    final Long taxGroupId = JdbcSupport.getLongDefaultToNullIfZero(rs, "taxGroupId");
                    TaxGroupData taxGroupData = null;
                    if (taxGroupId != null) {
                        taxGroupData = TaxGroupData.lookup(taxGroupId, null);
                    }

                    final BigDecimal nominalAnnualInterestRate = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs,
                            "nominalAnnualInterestRate");

                    final EnumOptionData interestCompoundingPeriodType = SavingsEnumerations.compoundingInterestPeriodType(
                            SavingsCompoundingInterestPeriodType.fromInt(JdbcSupport.getInteger(rs, "interestCompoundingPeriodType")));

                    final EnumOptionData interestPostingPeriodType = SavingsEnumerations.interestPostingPeriodType(
                            SavingsPostingInterestPeriodType.fromInt(JdbcSupport.getInteger(rs, "interestPostingPeriodType")));

                    final EnumOptionData interestCalculationType = SavingsEnumerations.interestCalculationType(
                            SavingsInterestCalculationType.fromInt(JdbcSupport.getInteger(rs, "interestCalculationType")));

                    final EnumOptionData interestCalculationDaysInYearType = SavingsEnumerations
                            .interestCalculationDaysInYearType(SavingsInterestCalculationDaysInYearType
                                    .fromInt(JdbcSupport.getInteger(rs, "interestCalculationDaysInYearType")));

                    final BigDecimal minRequiredOpeningBalance = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs,
                            "minRequiredOpeningBalance");

                    final Integer lockinPeriodFrequency = JdbcSupport.getInteger(rs, "lockinPeriodFrequency");
                    EnumOptionData lockinPeriodFrequencyType = null;
                    final Integer lockinPeriodFrequencyTypeValue = JdbcSupport.getInteger(rs, "lockinPeriodFrequencyType");
                    if (lockinPeriodFrequencyTypeValue != null) {
                        final SavingsPeriodFrequencyType lockinPeriodType = SavingsPeriodFrequencyType
                                .fromInt(lockinPeriodFrequencyTypeValue);
                        lockinPeriodFrequencyType = SavingsEnumerations.lockinPeriodFrequencyType(lockinPeriodType);
                    }

                    final boolean withdrawalFeeForTransfers = rs.getBoolean("withdrawalFeeForTransfers");

                    final boolean allowOverdraft = rs.getBoolean("allowOverdraft");
                    final BigDecimal overdraftLimit = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "overdraftLimit");
                    final BigDecimal nominalAnnualInterestRateOverdraft = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs,
                            "nominalAnnualInterestRateOverdraft");
                    final BigDecimal minOverdraftForInterestCalculation = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs,
                            "minOverdraftForInterestCalculation");

                    final BigDecimal minRequiredBalance = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "minRequiredBalance");
                    final boolean enforceMinRequiredBalance = rs.getBoolean("enforceMinRequiredBalance");
                    final BigDecimal maxAllowedLienLimit = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "maxAllowedLienLimit");
                    final boolean lienAllowed = rs.getBoolean("lienAllowed");
                    savingsAccountData = SavingsAccountData.instance(id, accountNo, depositType, externalId, null, null, null, null,
                            productId, null, null, null, status, subStatus, null, timeline, currency, nominalAnnualInterestRate,
                            interestCompoundingPeriodType, interestPostingPeriodType, interestCalculationType,
                            interestCalculationDaysInYearType, minRequiredOpeningBalance, lockinPeriodFrequency, lockinPeriodFrequencyType,
                            withdrawalFeeForTransfers, summary, allowOverdraft, overdraftLimit, minRequiredBalance,
                            enforceMinRequiredBalance, maxAllowedLienLimit, lienAllowed, minBalanceForInterestCalculation, onHoldFunds,
                            nominalAnnualInterestRateOverdraft, minOverdraftForInterestCalculation, withHoldTax, taxGroupData,
                            lastActiveTransactionDate, isDormancyTrackingActive, daysToInactive, daysToDormancy, daysToEscheat,
                            onHoldAmount);

                    savingsAccountData.setClientData(clientData);
                    savingsAccountData.setGroupGeneralData(groupGeneralData);
                    savingsAccountData.setSavingsProduct(savingsProductData);
                    savingsAccountData.setGlAccountIdForInterestOnSavings(glAccountIdForInterestOnSavings);
                    savingsAccountData.setGlAccountIdForSavingsControl(glAccountIdForSavingsControl);
                }

                if (!transMap.containsValue(transactionId)) {

                    final int transactionTypeInt = JdbcSupport.getInteger(rs, "transactionType");
                    final SavingsAccountTransactionEnumData transactionType = SavingsEnumerations.transactionType(transactionTypeInt);

                    final LocalDate date = JdbcSupport.getLocalDate(rs, "transactionDate");
                    final LocalDate balanceEndDate = JdbcSupport.getLocalDate(rs, "balanceEndDate");
                    final LocalDate transSubmittedOnDate = JdbcSupport.getLocalDate(rs, "createdDate");
                    final BigDecimal amount = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs, "transactionAmount");
                    final BigDecimal overdraftAmount = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs, "overdraftAmount");
                    final BigDecimal outstandingChargeAmount = null;
                    final BigDecimal runningBalance = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs, "runningBalance");
                    final boolean reversed = rs.getBoolean("reversed");
                    final boolean isManualTransaction = rs.getBoolean("manualTransaction");
                    final Long officeId = rs.getLong("officeId");
                    final BigDecimal cumulativeBalance = JdbcSupport.getBigDecimalDefaultToZeroIfNull(rs, "cumulativeBalance");

                    final boolean postInterestAsOn = false;

                    PaymentDetailData paymentDetailData = null;
                    if (transactionType.isDepositOrWithdrawal()) {
                        final Long paymentTypeId = JdbcSupport.getLong(rs, "paymentType");
                        if (paymentTypeId != null) {
                            final String typeName = rs.getString("paymentTypeName");
                            final PaymentTypeData paymentTypeData = new PaymentTypeData(paymentTypeId, typeName, null, false, null, null,
                                    false);
                            paymentDetailData = new PaymentDetailData(id, paymentTypeData, null, null, null, null, null);
                        }
                    }

                    savingsAccountTransactionData = SavingsAccountTransactionData.create(transactionId, transactionType, paymentDetailData,
                            id, accountNo, date, currency, amount, outstandingChargeAmount, runningBalance, reversed, transSubmittedOnDate,
                            postInterestAsOn, cumulativeBalance, balanceEndDate);
                    savingsAccountTransactionData.setOverdraftAmount(overdraftAmount);

                    transMap.put("id", transactionId);
                    if (savingsAccountData.getOfficeId() == null) {
                        savingsAccountData.setOfficeId(officeId);
                    }

                    savingsAccountData.setSavingsAccountTransactionData(savingsAccountTransactionData);
                }

                if (chargeId != null && !chargeDetails.containsValue(chargeId)) {
                    final boolean isPenalty = rs.getBoolean("isPenaltyCharge");
                    final BigDecimal chargeAmount = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "chargeAmount");
                    final Integer chargesTimeType = rs.getInt("chargeTimeType");
                    final EnumOptionData enumOptionDataForChargesTimeType = new EnumOptionData(chargesTimeType.longValue(), null, null);
                    final SavingsAccountChargeData savingsAccountChargeData = new SavingsAccountChargeData(chargeId, chargeAmount,
                            enumOptionDataForChargesTimeType, isPenalty);

                    final Long chargesPaidById = rs.getLong("chargesPaidById");
                    final BigDecimal chargesPaid = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "paidByAmount");
                    final SavingsAccountChargesPaidByData savingsAccountChargesPaidByData = new SavingsAccountChargesPaidByData(
                            chargesPaidById, chargesPaid);
                    savingsAccountChargesPaidByData.setSavingsAccountChargeData(savingsAccountChargeData);
                    if (savingsAccountChargesPaidByData != null) {
                        savingsAccountTransactionData.setChargesPaidByData(savingsAccountChargesPaidByData);
                    }

                    chargeDetails.put("id", chargeId);
                }

                if (taxDetailId != null && !taxDetails.containsValue(taxDetailId)) {
                    final BigDecimal amount = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "taxAmount");
                    final BigDecimal percentage = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "taxPercentage");
                    final Long debitId = rs.getLong("debitAccountId");
                    final Long creditId = rs.getLong("creditAccountId");
                    final GLAccountData debitAccount = GLAccountData.createFrom(debitId);
                    final GLAccountData creditAccount = GLAccountData.createFrom(creditId);

                    if (taxComponentId != null) {
                        final TaxComponentData taxComponent = TaxComponentData.createTaxComponent(taxComponentId, percentage, debitAccount,
                                creditAccount);
                        savingsAccountTransactionData.setTaxDetails(new TaxDetailsData(taxComponent, amount));
                    }

                    taxDetails.put("id", taxDetailId);
                }

            }
            if (savingsAccountData != null) {
                savingsAccountDataList.add(savingsAccountData);
            }
            return savingsAccountDataList;

            // final String productName = rs.getString("productName");

            // final String fieldOfficerName = rs.getString("fieldOfficerName");

            // final String submittedByUsername = rs.getString("submittedByUsername");
            // final String submittedByFirstname = rs.getString("submittedByFirstname");
            // final String submittedByLastname = rs.getString("submittedByLastname");
            //

            // final String rejectedByUsername = rs.getString("rejectedByUsername");
            // final String rejectedByFirstname = rs.getString("rejectedByFirstname");
            // final String rejectedByLastname = rs.getString("rejectedByLastname");
            //

            // final String withdrawnByUsername = rs.getString("withdrawnByUsername");
            // final String withdrawnByFirstname = rs.getString("withdrawnByFirstname");
            // final String withdrawnByLastname = rs.getString("withdrawnByLastname");

            // final String approvedByUsername = rs.getString("approvedByUsername");
            // final String approvedByFirstname = rs.getString("approvedByFirstname");
            // final String approvedByLastname = rs.getString("approvedByLastname");

            // final String activatedByUsername = rs.getString("activatedByUsername");
            // final String activatedByFirstname = rs.getString("activatedByFirstname");
            // final String activatedByLastname = rs.getString("activatedByLastname");

            // final String closedByUsername = rs.getString("closedByUsername");
            // final String closedByFirstname = rs.getString("closedByFirstname");
            // final String closedByLastname = rs.getString("closedByLastname");

            // final String currencyName = rs.getString("currencyName");
            // final String currencyNameCode = rs.getString("currencyNameCode");
            // final String currencyDisplaySymbol = rs.getString("currencyDisplaySymbol");

            /*
             * final BigDecimal withdrawalFeeAmount = rs.getBigDecimal("withdrawalFeeAmount");
             *
             * EnumOptionData withdrawalFeeType = null; final Integer withdrawalFeeTypeValue =
             * JdbcSupport.getInteger(rs, "withdrawalFeeTypeEnum"); if (withdrawalFeeTypeValue != null) {
             * withdrawalFeeType = SavingsEnumerations.withdrawalFeeType(withdrawalFeeTypeValue); }
             */

            /*
             * final BigDecimal annualFeeAmount = JdbcSupport.getBigDecimalDefaultToNullIfZero(rs, "annualFeeAmount");
             *
             * MonthDay annualFeeOnMonthDay = null; final Integer annualFeeOnMonth = JdbcSupport.getInteger(rs,
             * "annualFeeOnMonth"); final Integer annualFeeOnDay = JdbcSupport.getInteger(rs, "annualFeeOnDay"); if
             * (annualFeeAmount != null && annualFeeOnDay != null) { annualFeeOnMonthDay = new
             * MonthDay(annualFeeOnMonth, annualFeeOnDay); }
             *
             * final LocalDate annualFeeNextDueDate = JdbcSupport.getLocalDate(rs, "annualFeeNextDueDate");
             */

        }
