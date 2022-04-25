#The goal of this file is to import the client_resoring.R file into concerto and run it. You don't need to use this file
#for anything outside concerto. Look at the code in the eval block in test #86: Reuella Rescoring Test. This code is suppose
#to run inside that block and will fail if you try to run it on your machine outside concerto.


# delete any previous record of session_results_df
rm(session_results_df)
# create an empty dataframe to hold session ids and theta
session_results_df <- data.frame(session_id=integer(),
                                 theta = double())

#max_session = max(result$session_id)
# TODO: replace the 10 in the loop with the max_session based on the code provided by client. maybe replace max with count instead

for(desired_session_id in 1:10){
  #TODO: Coercion of NA when filtering needs to be fixed
  # filter result to grab the sessions that have the same session id as the desired session id
  one_test = filter(result, result$session_id == as.character(desired_session_id))
  # TODO: filter only transfers over data so we need to transfer names to get the headers (use rbind names from result to one test)
  print(names(one_test))
  print(one_test)

  x = vector()

  #try to remove any previous instance of params that may have been created
  tryCatch({
    rm(params)
  }, error = function(err){
    print(err)
  })

  #matrix is blank 2D array
  params = matrix(,nrow =0 , ncol = 4)

  #headers for param (because A, B, C, D are the options in tests)
  dimnames(params) = list(c(),c("a","b","c","d"))

  #for as many session id's are there in one_test loop over them
  for (i in 1:length(one_test[['session_id']])){
    tryCatch({
      score = one_test[['score']][[1]]
      print("score")
      print(score)
      question_id = one_test[['item_id']][[1]]
      print("question_id")
      print(question_id)
      p1 = 2
      p2 = 0
      p3 = 0.25
      p4 = 1
      x = append(x,score)
      #rbind auto generates the columns and the data you are trying to bind creates new rows
      params <- rbind(params,c(p1,p2,p3,p4))
      print("params")
      print(params)
    }, error = function(err){
      print(err)
    })
 }
   if (length(x)>35){
   #TODO: get the thetaEst function from Dr. Gordon and set new_theta to the result from the function. I've used an arbitrary float for now for value of new theta
    new_theta = 0.46785
    #basically you replace the existing theta for the session with the new theta you generated
    session_id = desired_session_id
    theta = new_theta
     # create a new data frame which we append to our list of session results
    session_data <- data.frame(session_id,theta)
    session_results_df <- rbind(session_results_df,session_data)
  }
}


############################################
#Start of loop
############################################

for (k in 1:10){
  #print('k')
  #print(k)

  ############################################
  # Determine the Difficulty/Discernment of the questions
  ############################################


  """
  Because of the way concerto nodes work. We get the variable result from the data manipulation node in concerto.
  In the client's recoring node this is actually called answer_data.

  results is an empty list we populate
  result is the answers_data data frame
  """
  # test_question_instance = 1
  results = list()

  #result is assesment response data table which is the answers_data
  #results is an empty list we use


  # TODO: once you solve the todo's before this line. The code from here on needs to be fixed to work inside concerto.
  # TODO: eventually you will need to write to a data frame with the new scores of questions
  #Loop through each line from the results file and put the theta from the test and the answer in a list with the number being the question number
  for (b in 1:length(result$item_id)){
    #get the session_id, question_id, and result
    session_id = result$session_id[[b]]
    question_number = result$item_id[[b]]
    if (question_number > 4800){
      question_number = 4801 + question_number %% 5
    } else {
      if(question_number > 4000){
        question_number = 4001 + question_number %% 6
      }
    }
    result_score = result$score[[b]]
    #print(c(session_id,question_number,result_score))


    #if the session_id is in the session results file
    if (session_id%in%session_results_df$session_id){

      #get the theta value corresponding to the session_id
      theta = as.numeric(session_results_df$theta[[match(session_id,session_results_df$session_id)]])

      # No idea what is happening
      if (length(results)<question_number){
        #results[[question_number]]
        results[[question_number]] = list()
      }
      #length(results[[question_number]])
      results[[question_number]][[length(results[[question_number]])+1]]=list(theta,result_score)

    }
  }
}

  ####### Now Rescore the questions
  # Don't score it if it has less than this number of responses
  min_questions = 5

  for (q in 1:length(results)){
    print(q)
    print(results[[q]])
    if (length(results[[q]])>min_questions){

      discernment = question_table$p1[question_table$id==q]
      difficulty = question_table$p2[question_table$id==q]

      sorted_data = results[[q]][order(sapply(results[[q]],'[[',1))]
      # print(sorted_data)

      number_of_bins = 5
      bin_size = 5

      number_of_bins = ceiling(length(results[[q]])/bin_size)

      j=0
      binned_theta = integer(number_of_bins)
      binned_score = integer(number_of_bins)
      count = integer(number_of_bins)
      for (j in 1:length(sorted_data)){
        bin = ceiling(j/(length(sorted_data)/number_of_bins))
        binned_theta[bin] = (binned_theta[bin]*count[bin] + sorted_data[[j]][[1]])/(count[bin]+1)
        binned_score[bin] = (binned_score[bin]*count[bin] + sorted_data[[j]][[2]])/(count[bin]+1)
        count[bin] = count[bin] + 1
      }

      stored_count = count

      Binned_Score_Data <- vector()
      Binned_Theta_Data <- vector()

      for (bin in 1:number_of_bins){
        while (count[bin] > 0){
          Binned_Theta_Data <- c(Binned_Theta_Data,binned_theta[bin])
          Binned_Score_Data <- c(Binned_Score_Data,binned_score[bin])
          count[bin] = count[bin]-1
        }
      }

      x = Binned_Theta_Data
      y = Binned_Score_Data



      tryCatch({
        discernment_param_start = question_table$p1[[match(q,question_table$id)]]
        diff_param_start = question_table$p2[[match(q,question_table$id)]]
      }, error = function(err){
        discernment_param_start = 2
        diff_param_start = 1
      })


      Func <- function(x,discernment_param,diff_param){0.25 + (1-0.25)/(1+exp(-discernment_param*(x-diff_param)))}



      tryCatch({
        fit <- nls(y~Func(x,discernment_param,diff_param),start=list(discernment_param=discernment_param_start, diff_param=discernment_param_start),algorithm="port",lower=c(0,-4),upper=c(3,4),control = list(maxiter=1000, warnOnly=T))
        discernment = summary(fit)$coefficients[1,1]
        difficulty = summary(fit)$coefficients[2,1]
      }, warning = function(w){
        # summary(fit)

        discernment = question_table$p1[question_table$id==q]
        difficulty = question_table$p2[question_table$id==q]

        tryCatch({
          discernment_param_start=coef(summary(fit))["discernment_param","Estimate"]
          diff_param_start=coef(summary(fit))["diff_param","Estimate"]

          fit <- nls(y~Func(x,discernment_param,diff_param),start=list(discernment_param=discernment_param_start, diff_param=diff_param_start),algorithm="port",lower=c(0,-4),upper=c(3,4),control = list(maxiter=1000, warnOnly=T))

          discernment = summary(fit)$coefficients[1,1]
          difficulty = summary(fit)$coefficients[2,1]


        }, warning = function(w){
          discernment = question_table$p1[question_table$id==q]
          difficulty = question_table$p2[question_table$id==q]
        },error = function(e){
          discernment = question_table$p1[question_table$id==q]
          difficulty = question_table$p2[question_table$id==q]}
        )
      }, error = function(e){
        discernment = question_table$p1[question_table$id==q]
        difficulty = question_table$p2[question_table$id==q]
      }
      )

      question_table <- within(question_table,p1[id==q]<-discernment)
      question_table <- within(question_table,p2[id==q]<-difficulty)


    }
  }
