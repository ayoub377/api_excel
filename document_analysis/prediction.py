from transformers import TapasTokenizer, TapasForQuestionAnswering
import pandas as pd


class TapasInference:
    def __init__(self, model_name="google/tapas-base-finetuned-wtq"):
        self.model = TapasForQuestionAnswering.from_pretrained(model_name)
        self.tokenizer = TapasTokenizer.from_pretrained(model_name)

    def predict(self, table, queries):

        inputs = self.tokenizer(table=table, queries=queries, padding="max_length", return_tensors="pt")
        outputs = self.model(**inputs)

        predicted_answer_coordinates, predicted_aggregation_indices = self.tokenizer.convert_logits_to_predictions(
            inputs, outputs.logits.detach(), outputs.logits_aggregation.detach()
        )
        print("Predicted answer coordinates: ", predicted_answer_coordinates)
        id2aggregation = {0: "NONE", 1: "SUM", 2: "AVERAGE", 3: "COUNT"}
        aggregation_predictions_string = [id2aggregation[x] for x in predicted_aggregation_indices]

        answers = []
        for coordinates in predicted_answer_coordinates:
            if len(coordinates) == 1:
                answers.append(table.iat[coordinates[0]])
            else:
                cell_values = [table.iat[coordinate] for coordinate in coordinates]
                answers.append(", ".join(cell_values))

        result = []
        for query, answer, predicted_agg in zip(queries, answers, aggregation_predictions_string):
            result.append({
                "query": query,
                "predicted_answer": answer if predicted_agg == "NONE" else f"{predicted_agg} > {answer}"
            })

        return result
