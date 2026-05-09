using Microsoft.Azure.CognitiveServices.Vision.Face;
using Microsoft.Azure.CognitiveServices.Vision.Face.Models;

namespace FaceAPI
	{
	public class SimilarFaceFinder
		{
		private readonly IFaceClient _faceApiClient;

		// Recognition model 4 was released in 2021 February.
		// It is recommended since its accuracy is improved over models 1, 2 y 3
		private static readonly string _recognitionModelName = RecognitionModel.Recognition04.ToString();

		private static readonly string _detectionModelName = DetectionModel.Detection03;

		public SimilarFaceFinder(IFaceClient faceClient)
			{
			this._faceApiClient = faceClient;
			}

		private static IFaceClient GetFaceApiClient(string endpoint, string key)
			{
			return new FaceClient(new ApiKeyServiceClientCredentials(key)) { Endpoint = endpoint };
			}
				
		public async Task FindSimilarFacesAsync(string referenceImagePath, List<string> similarImagesPaths)
			{
			IList<Guid?> targetFaceIds = new List<Guid?>();
			foreach(string path in similarImagesPaths)
				{
				List<DetectedFace> detectedFaces = await this.DetectFaces(path);
				targetFaceIds.Add(detectedFaces[0].FaceId.Value);
				}

			List<DetectedFace> referenceFace = await this.DetectFaces(referenceImagePath);

			// Find a similar face(s) in the list of IDs. Comapring only the first in list for testing purposes.
			IList<SimilarFace> similarResults = await this._faceApiClient.Face.FindSimilarAsync(referenceFace[0].FaceId.Value, null, null, targetFaceIds);
			foreach (SimilarFace similarResult in similarResults)
				{
				Console.WriteLine($"Face ID:{similarResult.FaceId} is similar with confidence: {similarResult.Confidence}.");
				}
			Console.WriteLine();
			}

		private async Task<List<DetectedFace>> DetectFaces(string imagePath)
			{
			IList<DetectedFace> detectedFaces = await this._faceApiClient.Face.DetectWithUrlAsync
					(
					url: imagePath,
					// It's mandatory to set this parameter to true in order to recognize and id faces
					// The identifier is assigned by the algorithm and stored in Azure for 24 hours.
					returnFaceId: true, 
					returnFaceLandmarks: false,
					returnFaceAttributes: new List<FaceAttributeType>() { FaceAttributeType.QualityForRecognition },
					detectionModel: _detectionModelName,
					// Recognition model must be set to recognition_03 or recognition_04 as a result
					recognitionModel: _recognitionModelName
					);

			List<DetectedFace> sufficientQualityFaces = new List<DetectedFace>();
			foreach (DetectedFace detectedFace in detectedFaces)
				{
				var faceQualityForRecognition = detectedFace.FaceAttributes.QualityForRecognition;
				if (faceQualityForRecognition.HasValue && (faceQualityForRecognition.Value >= QualityForRecognition.Medium))
					{
					sufficientQualityFaces.Add(detectedFace);
					Console.WriteLine($"Face in {imagePath} has been assigned the ID: {detectedFace.FaceId.Value}");
					}
				}

			//Console.WriteLine($"{detectedFaces.Count} face(s) with {sufficientQualityFaces.Count} having sufficient quality for recognition detected from image {imagePath}");

			return sufficientQualityFaces;
			}
		}
	}

