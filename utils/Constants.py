# General validation constants
CONF_MAIN = 'Main'
CONF_ARX = 'ARX'
K_ANONYMITY = 'kanonymity'
L_DIVERSITY = 'ldiversity'
IDENTIFYING = 'id_columns'
QUASI_IDENTIFYING = 'qi_columns'
SENSITIVE_ATTRIBUTES = 'sa_columns'
IN = 'in'
OUT = 'out'
EMPTY_WHERE = '1 = 1'

# Summary statistics module
SUMMARY_STATISTICS = 'Summary statistics'
SS_INPUT = 'Input statistics'
SS_OUTPUT = 'Output statistics'
SS_DISTINCT = 'Distinct values'
SS_INFORMATIVE = 'Informative measures'
SS_MODES = 'Modes'
SS_GENSUP = 'Generalized or suppressed'
SS_SUP = 'Suppressed'
SS_TOTAL_GENSUP = 'Total generalized or suppressed'
SS_TOTAL_SUP = 'Total suppressed'
SS_SUP_OF_CHANGED = 'Suppressed of total changed'


# Equivalence class module
EQUIVALENCE_CLASSES = 'Equivalence class statistics'
# Inner keys
EQ_INPUT = 'Input equivalence class'
EQ_OUTPUT = 'Output equivalence class'
EQ_AVG_SUP = 'Average equivalence class size (including suppressed)'
EQ_AVG_NOSUP = 'Average equivalence class size (without suppressed)'
EQ_BIGGEST = 'Biggest equivalence class size'
EQ_SUPPRESSED = 'Completely suppressed class size'
EQ_NOCLASSES = 'Number of classes'
EQ_NORECORDS = 'Number of records'
EQ_SMALLEST = 'Smallest equivalence class size'

# Privacy verification module
PRIVACY_VERIFICATION = 'Privacy model verification'
# Inner keys
PR_K = 'K and violations'
PR_L = 'L and violations'
PR_XY = 'XY and violations'

# Attack model risk analysis module
ATTACK_RISKS = 'Attacker model risks'
# Inner keys
AR_INPUT = 'Input attacker model risks'
AR_OUTPUT = 'Output attacker model risks'
AR_RECORDS_AFFECTED_LOWEST = 'Records affected by lowest risk'
AR_RECORDS_AFFECTED_HIGHEST = 'Records affected by highest risk'
AR_MARKETER = 'Marketer risks'
AR_ESTIMATED_MARKETER_RISK = 'Estimated marketer risk'
AR_PROSECUTOR = 'Prosecutor risks'
AR_PROSECUTOR_LOWEST = 'Lowest prosecutor risk'
AR_PROSECUTOR_AVERAGE = 'Average prosecutor risk'
AR_PROSECUTOR_HIGHEST = 'Highest prosecutor risk'
AR_JOURNALIST = 'Journalist risks'
AR_ESTIMATED_JOURNALIST_RISK = 'Estimated journalist risk'
AR_ESTIMATED_PROSECUTOR_RISK = 'Estimated prosecutor risk'
AR_RECORDS_AT_RISK = 'Records at risk'
AR_HIGHEST_RISK = 'Highest risk'
AR_SUCCESS_RATE = 'Success rate'
AR_OVERVIEW = 'Overview'