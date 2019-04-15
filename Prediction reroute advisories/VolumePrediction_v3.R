################################One-Hot Encoding#############################################
##traffic data 
#https://aspm.faa.gov/opsnet/sys/main.asp


##Load data
me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/Traffic_and_reroutes_Logic_reduced_v1.csv")




#####Month########

for(unique_value in unique(me$Month)){me[paste("Month", unique_value, sep = ".")] <- ifelse(me$Month == unique_value, 1, 0)}

#####artcc########

for(unique_value in unique(me$ARTCC)){me[paste("ARTCC", unique_value, sep = ".")] <- ifelse(me$ARTCC == unique_value, 1, 0)}


for(unique_value in unique(me$Day)){me[paste("Day", unique_value, sep = ".")] <- ifelse(me$Day == unique_value, 1, 0)}

#####Hour########

for(unique_value in unique(me$Hour)){me[paste("Hour", unique_value, sep = ".")] <- ifelse(me$Hour == unique_value, 1, 0)}


write.csv(me,file = "C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced_v1.csv" )






#######################Decision Tree##################
me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
#me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced_v1.csv")
me$X<-NULL
#me$Day<-NULL
#me$Traffic.Count<-NULL
me$Reroute<-NULL
#me$Type<-NULL
str(me)
me[7:85]<-NULL
#me[6:86]<-NULL ##when remove traffic count
str(me)
len<-nrow(me)
len50<-len*0.5
len75<-len*0.75
set.seed(123)
ts<-sample(len)
train<-me[ts[1:len50],]
val<-me[ts[(len50+1):len75],]
test<-me[ts[(len75+1):len],]
library(C50)
M<-C5.0(train[-6],train$Type,trials = 10)
#M<-C5.0(train[-5],train$Reroute,trials = 10) ## when remove traffic count
M
summary(M)
pred<-predict(M,val)
summary(pred)
library(gmodels)
CrossTable(val$Type,pred,prop.r = FALSE,prop.c = FALSE,prop.chisq = FALSE,dnn = c('Actual Event','Predicted Event'))

P<-predict(M,test)
summary(P)
CrossTable(test$Type,P,prop.r = FALSE,prop.c = FALSE,prop.chisq = FALSE,dnn = c('Actual Event','Predicted Event'))

library(caret)
confusionMatrix(pred,val$Type)
confusionMatrix(P,test$Type)

MCC = ((TP * TN)-(FP*FN))/sqrt((TP+FN)*(TP+FP)*(TN+FP)*(TN+FN))


################################k-nn#############################################
me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
#me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced_v1.csv")
me$X<-NULL
me$Month<-NULL
me$ARTCC<-NULL
me$Hour<-NULL
me$Day<-NULL
me$Type<-NULL
str(me)
#me_z<-as.data.frame(scale(me[1])) ##normalize
#normalize<- function(x){return((x-min(x))/(max(x)-min(x)))}
me_z<-as.data.frame(me[1], normalize)
me[1]<-me_z
str(me)
set.seed(123)
len<-nrow(me)
len50<-len*0.5
len75<-len*0.75
ts<-sample(len)
train<-me[ts[1:len50],]
val<-me[ts[(len50+1):len75],]
test<-me[ts[(len75+1):len],]
trainl<-me[ts[1:len50],2]
vall<-me[ts[(len50+1):len75],2]
testl<-me[ts[(len75+1):len],2] 
#install.packages("class")
library(class)
vp<-knn(train = train,test = val,cl=trainl,k=sqrt(len))
library(gmodels)
CrossTable(x=vall,y=vp,prop.chisq = FALSE)
library(caret)
confusionMatrix(vp,vall)
tp<-knn(train = train,test = test,cl=trainl,k=sqrt(len)) ### how to choose k ?? see : https://discuss.analyticsvidhya.com/t/how-to-choose-the-value-of-k-in-knn-algorithm/2606/8
CrossTable(x=testl,y=tp,prop.chisq = FALSE)
confusionMatrix(tp,testl)

MCC = ((TP * TN)-(FP*FN))/sqrt((TP+FN)*(TP+FP)*(TN+FP)*(TN+FN))

me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
me$X<-NULL
me$Month<-NULL
me$ARTCC<-NULL
me$Day<-NULL
me$Hour<-NULL
me$Type<-NULL
me_z<-as.data.frame(scale(me[-2]))
len<-nrow(me)
len50<-len*0.5
len75<-len*0.75
set.seed(123)
ts<-sample(len)
train<-me_z[ts[1:len50],]
val<-me_z[ts[(len50+1):len75],]
test<-me_z[ts[(len75+1):len],]
trainl<-me[ts[1:len50],2]
vall<-me[ts[(len50+1):len75],2]
testl<-me[ts[(len75+1):len],2] 
#install.packages("class")
library(class)
vp<-knn(train = train,test = val,cl=trainl,k=sqrt(len))
library(gmodels)
CrossTable(x=vall,y=vp,prop.chisq = FALSE)
library(caret)
confusionMatrix(vp,vall)
tp<-knn(train = train,test = test,cl=trainl,k=3)
CrossTable(x=testl,y=tp,prop.chisq = FALSE)
confusionMatrix(tp,testl)
###############################Naive Bayes##############################
me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
me$X<-NULL
me$Reroute<-NULL
#me$Type<-NULL
me[7:85]<-NULL
str(me)
len<-nrow(me)
len50<-len*0.5
len75<-len*0.75
set.seed(123)
ts<-sample(len)
train<-me[ts[1:len50],]
val<-me[ts[(len50+1):len75],]
test<-me[ts[(len75+1):len],]
trainl<-me[ts[1:len50],6]
vall<-me[ts[(len50+1):len75],6]
testl<-me[ts[(len75+1):len],6]
#install.packages("e1071")
library(e1071)
met<-naiveBayes(train[-6],trainl,laplace=1)
mep<-predict(met,val)
#install.packages("gmodels")
library(gmodels)
CrossTable(mep,vall,prop.chisq = FALSE,prop.t = FALSE,dnn = c('Predicted Event','Actual Event'))
library(caret)
confusionMatrix(mep,vall)

mep2<-predict(met,test,laplace=1)
CrossTable(mep2,testl,prop.chisq = FALSE,prop.t = FALSE,dnn = c('predicted','actual'))
confusionMatrix(mep2,testl)


########################SVM######################

me<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
me$X<-NULL
me$Month<-NULL
me$ARTCC<-NULL
me$Hour<-NULL
me$Day<-NULL
me$Reroute<-NULL
str(me)
len<-nrow(me)
len50<-len*0.5
len75<-len*0.75
set.seed(123)
ts<-sample(len)
train<-me[ts[1:len50],] #50% of the dataset
val<-me[ts[(len50+1):len75],] #25%
test<-me[ts[(len75+1):len],]
library(e1071)
#install.packages("kernlab")
library(kernlab)

N<-ksvm(Type ~ ., data = train, kernel= "rbfdot")
Nv<- predict(N,val)
table(Nv,val$Type)
confusionMatrix(Nv,val$Type)

Nt<- predict(N,test)
table(Nt,test$Type)
confusionMatrix(Nt,test$Type)


########################Bagging Ensembles###########
BaData<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
#BaData<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced_v1.csv")
BaData$X<-NULL
#BaData$Type<-NULL
BaData$Reroute<-NULL
BaData[7:85]<-NULL
len<-nrow(BaData)
len50<-len*0.5
len75<-len*0.75
set.seed(123)

ts<-sample(len)
tr<-BaData[ts[1:len50],] #50% of the dataset
va<-BaData[ts[(len50+1):len75],] #25%
te<-BaData[ts[(len75+1):len],]
library(ipred)

#Bamodel<-bagging(Type ~.,data = tr,nbagg = 25)
#Bava<-predict(Bamodel,va)
#Bava$class<-factor(Bava$class)

#confusionMatrix(Bava$class,va$Type)

Bamodel<-bagging(Type ~.,data = tr,nbagg = 25)
Bava<-predict(Bamodel,va)
#Bava$class<-factor(Bava$class)
library(caret)
confusionMatrix(Bava,va$Type)

Bate<-predict(Bamodel,te)

confusionMatrix(Bate,te$Type)



########################Boosting Ensembles###########
BoData<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
#BoData<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced_v1.csv")
BoData$X<-NULL
#BoData$Type<-NULL
BoData$Reroute<-NULL
BoData[7:85]<-NULL
len<-nrow(BoData)
len50<-len*0.5
len75<-len*0.75
set.seed(123)
ts<-sample(len)
tr<-BoData[ts[1:len50],] #50% of the dataset
va<-BoData[ts[(len50+1):len75],] #25%
te<-BoData[ts[(len75+1):len],]
#install.packages('adabag')
library(adabag)

Bomodel<-boosting(Type ~.,data = tr)
Bova<-predict(Bomodel,va)
Bova$class<-factor(Bova$class)
confusionMatrix(Bova$class,va$Type)

Bote<-predict(Bomodel,te)
Bote$class<-factor(Bote$class)
confusionMatrix(Bote$class,te$Type)



########################Random Forest###########
RFData<-read.csv("C:/Users/teman/OneDrive - Georgia Institute of Technology/Master Thesis/Data Processing/Prediction/rerouteDataLogic_reduced.csv")
RFData$X<-NULL
RFData$Type<-NULL
#RFData$Reroute<-NULL
RFData[7:85]<-NULL
len<-nrow(RFData)
len50<-len*0.5
len75<-len*0.75
set.seed(123)
ts<-sample(len)
tr<-RFData[ts[1:len50],] #50% of the dataset
va<-RFData[ts[(len50+1):len75],] #25%
te<-RFData[ts[(len75+1):len],]
#install.packages('randomForest')
library(randomForest)
RFmodel<-randomForest(Reroute ~.,data = tr)
RFva<-predict(RFmodel,va)
confusionMatrix(RFva,va$Reroute)

RFte<-predict(RFmodel,te)
confusionMatrix(RFte,te$Reroute)

