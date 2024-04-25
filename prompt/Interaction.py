

class InteractionPrompt():

    U_interaction_prompt = """        
        Respond to a senior expert's query on movie recommendation serendipity, using the user portrait and\
        movie analyst insight {movie_analyst_response}: {}. Focus on the user's perspective in your analysis. 
        Here is the query asked from senior expert {query}: {}
        """

    I_interaction_prompt = """       
        Respond to a senior expert's query on movie recommendation serendipity, using the user portrait and\
        user analyst insight {user_analyst_response}: {}. Focus on the movie's perspective in your analysis. 
        Here is the query asked from senior expert {query}: {}
        """

    # 让 E Agent生成query然后组合，U/I 应该各一个
    EG_interaction_prompt = """
        Upon reviewing the responses from the user analyst: {} and movie analyst: {}, your task is to use the report\
        provided to assess whether the recommendations can evaluate users' serendipity of the recommended movies.
        To achieve this goal to need to summarize these report first. 

        And then, If you believe the information provided by the user and movie analyst is insufficient for a comprehensive assessment, \
        detail your queries accordingly. If the provided analyses are sufficient, simply indicate with "NaN".
        
        Follow the format below for your output:

        Summary:
        {{Give the summary of two reports.}}

        Query for user analyst:
        {{Write the specified query for user analyst here, if not write "NaN" here.}}

        Query for movie analyst:
        {{Write the specified query for movie analyst here, if not write "NaN" here.}}
        """