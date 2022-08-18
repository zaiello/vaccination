
library("ggrepel")
library("rjson")
setwd("~/Downloads/ST517")
result <- read.csv(file = "covid_data.csv")
result_json <- fromJSON(file = "covid_data.json")
library(ggplot2)
library(backports)
library(broom)

# A plot of the data
ggplot(result_json, aes(x=administered_dose1_pop_pct, y=conf_cases)) + 
  geom_point() + 
  ggrepel::geom_text_repel(aes(label = state)) + 
  labs(x = '% of Population With At Least One Dose', y ='Confirmed Cases')

#linear model, administered_dose1_pop_pct is the explanatory variable
slr_covid <- lm(conf_cases~administered_dose1_pop_pct, data = result)
summary(slr_covid)

# Estimate B0: 351191, estimate B1: 3082, estimate SE: 535400

# Replot points but this time with the regression line overlaid
ggplot(result, aes(x=administered_dose1_pop_pct, y=conf_cases)) + 
  geom_point() + 
  ggrepel::geom_text_repel(aes(label = state)) + 
  labs(x = '% of Population With At Least One Dose', y ='Confirmed Cases') +
  geom_smooth(method = "lm")
#Constant variance assumption appears to be violated

# Evaluate the validity of the model using residuals
covid_diag <- augment(slr_covid)
qplot(conf_cases, .resid, data=covid_diag)
qplot(.fitted, .resid, data = covid_diag)

# First plot shows a systematic change in the variance across COVID cases 
# Let's do a lack of fit F test
mod_sep_covid <- lm(log(conf_cases)~factor(administered_dose1_pop_pct), data = result)
mod_slr_covid <- lm(log(conf_cases)~ administered_dose1_pop_pct, data = result)
anova(mod_slr_covid, mod_sep_covid)

# p = 0, the SLR model is not adequate