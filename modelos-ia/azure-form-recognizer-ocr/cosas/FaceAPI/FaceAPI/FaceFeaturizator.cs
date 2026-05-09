using Microsoft.Azure.CognitiveServices.Vision.Face;
using Microsoft.Azure.CognitiveServices.Vision.Face.Models;

namespace FaceAPI
	{
	public class FaceFeaturizator
		{
		private readonly IFaceClient _faceApiClient;

		// Recognition model 4 was released in 2021 February.
		// It is recommended since its accuracy is improved over models 1, 2 y 3
		private static readonly string _recognitionModelName = RecognitionModel.Recognition04.ToString();

		private static readonly string _detectionModelName = DetectionModel.Detection01;

		public FaceFeaturizator(IFaceClient faceClient)
			{
			this._faceApiClient = faceClient;
			}

		private static IFaceClient GetFaceApiClient(string endpoint, string key)
			{
			return new FaceClient(new ApiKeyServiceClientCredentials(key)) { Endpoint = endpoint };
			}

		public async Task AnalyzeFacesInImageAsync(string imagePath, bool extractFaceLandmarks, IList<FaceAttributeType> requestedFaceAttribs)
			{
			IList<DetectedFace> detectedFaces = await DetectFaces(imagePath,extractFaceLandmarks, requestedFaceAttribs);
			
			Console.WriteLine($"{detectedFaces.Count} face(s) detected from image {imagePath}");

			foreach (var detectedFace in detectedFaces)
				{
				ExtractFaceInfo(detectedFace, imagePath);
				}
			}

		private async Task<List<DetectedFace>> DetectFaces(string imagePath, bool extractFaceLandmarks, IList<FaceAttributeType> requestedFaceAttribs)
			{
			IList<DetectedFace> detectedFaces = await this._faceApiClient.Face.DetectWithUrlAsync
				(
				url: imagePath, //	File.OpenRead(Path.Combine(Environment.CurrentDirectory, "foto.jpg")),
				returnFaceId: false,
				returnFaceLandmarks: extractFaceLandmarks,
				returnFaceAttributes: requestedFaceAttribs,
				// We specify detection model 1 because we are retrieving attributes.
				detectionModel: _detectionModelName,
				recognitionModel: _recognitionModelName
				);

			List<DetectedFace> sufficientQualityFaces = new List<DetectedFace>();
			foreach (DetectedFace detectedFace in detectedFaces)
				{
				var faceQualityForRecognition = detectedFace.FaceAttributes.QualityForRecognition;
				if (faceQualityForRecognition.HasValue && (faceQualityForRecognition.Value >= QualityForRecognition.Medium))
					{
					sufficientQualityFaces.Add(detectedFace);
					}
				}

			Console.WriteLine($"{detectedFaces.Count} face(s) with {sufficientQualityFaces.Count} having sufficient quality for recognition detected from image {imagePath}");

			return sufficientQualityFaces;
			}

		private static void ExtractFaceInfo(DetectedFace detectedFace, string imageFileName)
			{
			// Parse and print all attributes of each detected face.
			Console.WriteLine($"Face attributes for {imageFileName}:");

			GetFaceBoudingBox(detectedFace);
			GetFaceAccesories(detectedFace);
			GetFaceEmotions(detectedFace);
			GetFaceAttributes(detectedFace);


			// Get quality for recognition attribute
			Console.WriteLine($"QualityForRecognition : {detectedFace.FaceAttributes.QualityForRecognition}");
			Console.WriteLine();
			}

		private static void GetFaceBoudingBox(DetectedFace detectedFace)
			{
			// Get bounding box of the faces
			Console.WriteLine($"Rectangle(Left/Top/Width/Height) : {detectedFace.FaceRectangle.Left} {detectedFace.FaceRectangle.Top} {detectedFace.FaceRectangle.Width} {detectedFace.FaceRectangle.Height}");
			}

		private static void GetFaceAccesories(DetectedFace detectedFace)
			{
			// Get accessories of the faces
			foreach (Accessory accessory in detectedFace.FaceAttributes.Accessories)
				{
				Console.WriteLine($"{accessory.Type} - Confidence: {accessory.Confidence}");
				}
			}

		private static void GetFaceEmotions(DetectedFace detectedFace)
			{
			// Get emotion on the face
			string emotionType = string.Empty;
			double emotionValue = 0.0;
			Emotion emotion = detectedFace.FaceAttributes.Emotion;
			if (emotion.Anger > emotionValue) { emotionValue = emotion.Anger; emotionType = "Anger"; }
			if (emotion.Contempt > emotionValue) { emotionValue = emotion.Contempt; emotionType = "Contempt"; }
			if (emotion.Disgust > emotionValue) { emotionValue = emotion.Disgust; emotionType = "Disgust"; }
			if (emotion.Fear > emotionValue) { emotionValue = emotion.Fear; emotionType = "Fear"; }
			if (emotion.Happiness > emotionValue) { emotionValue = emotion.Happiness; emotionType = "Happiness"; }
			if (emotion.Neutral > emotionValue) { emotionValue = emotion.Neutral; emotionType = "Neutral"; }
			if (emotion.Sadness > emotionValue) { emotionValue = emotion.Sadness; emotionType = "Sadness"; }
			if (emotion.Surprise > emotionValue) { emotionType = "Surprise"; }
			Console.WriteLine($"Emotion : {emotionType}");
			}

		private static void GetFaceAttributes(DetectedFace detectedFace)
			{
			// Get face attributes
			Console.WriteLine($"Age : {detectedFace.FaceAttributes.Age}");
			Console.WriteLine($"Blur : {detectedFace.FaceAttributes.Blur.BlurLevel}");
			Console.WriteLine($"Exposure : {detectedFace.FaceAttributes.Exposure.ExposureLevel}");
			Console.WriteLine($"FacialHair : {string.Format($"{0}", detectedFace.FaceAttributes.FacialHair.Moustache + detectedFace.FaceAttributes.FacialHair.Beard + detectedFace.FaceAttributes.FacialHair.Sideburns > 0 ? "Yes" : "No")}");
			Console.WriteLine($"Glasses : {detectedFace.FaceAttributes.Glasses}");
			Console.WriteLine($"Hair : {GetHairColor(detectedFace)}");
			Console.WriteLine($"HeadPose : {string.Format("Pitch: {0}, Roll: {1}, Yaw: {2}", Math.Round(detectedFace.FaceAttributes.HeadPose.Pitch, 2), Math.Round(detectedFace.FaceAttributes.HeadPose.Roll, 2), Math.Round(detectedFace.FaceAttributes.HeadPose.Yaw, 2))}");
			Console.WriteLine($"Makeup : {string.Format("{0}", (detectedFace.FaceAttributes.Makeup.EyeMakeup || detectedFace.FaceAttributes.Makeup.LipMakeup) ? "Yes" : "No")}");
			Console.WriteLine($"Noise : {detectedFace.FaceAttributes.Noise.NoiseLevel}");
			Console.WriteLine
				(
				$"Occlusion : {string.Format("EyeOccluded: {0}", detectedFace.FaceAttributes.Occlusion.EyeOccluded ? "Yes" : "No")} " +
				$" {string.Format("ForeheadOccluded: {0}", detectedFace.FaceAttributes.Occlusion.ForeheadOccluded ? "Yes" : "No")}   " +
				$"{string.Format("MouthOccluded: {0}", detectedFace.FaceAttributes.Occlusion.MouthOccluded ? "Yes" : "No")}");
			Console.WriteLine($"Smile : {detectedFace.FaceAttributes.Smile}"
			);
			}

		private static string GetHairColor(DetectedFace detectedFace)
			{
			Hair detectedHair = detectedFace.FaceAttributes.Hair;
			HairColorType colorType = HairColorType.Unknown;
			string detectedHairColor = "Unknown";

			if (detectedHair.Invisible)
				{
				detectedHairColor = "Not visible";
				}
			else if (detectedHair.HairColor.Count == 0)
				{
				detectedHairColor = "Bald";
				}
			else
				{

				double maxConfidence = 0.0f;

				foreach (HairColor hairColor in detectedHair.HairColor)
					{
					if (hairColor.Confidence > maxConfidence)
						{
						maxConfidence = hairColor.Confidence;
						colorType = hairColor.Color;
						detectedHairColor = colorType.ToString();
						}
					}
				}

			return detectedHairColor;
			}
		}
	}




		//public async Task Main(string[] args)
		//	{
		//	// Detect - get features from faces.
		//	await FeaturizeFaceAsync(client, ImageBaseUrl, RecognitionModel4);
		//	}

		//private async Task<IList<DetectedFace>> DetectFacesAsync(List<string> imagePaths)
		//	{
		//	List<DetectedFace> detectedFaces = new();
		//	foreach (string path in imagePaths)
		//		{
		//		DetectedFace detectedFace = await this.AnalyzeImageAsync(path);
		//		detectedFaces.Add(detectedFace);
		//		}
		//	return detectedFaces;
		//	}

		

		//private static async Task FeaturizeFaceAsync(DetectedFace detectedFace)
		//	{
		//	}



		//private static async Task FeaturizeFaceAsync(IFaceClient client, string url, string recognitionModel)
		//	{
		//	foreach (var imageFileName in _imageFileNames)
		//		{
		//		IList<DetectedFace> detectedFaces;

		//		//detectedFaces = await client.Face.DetectWithStreamAsync
		//		//	(
		//		//	File.OpenRead(Path.Combine(Environment.CurrentDirectory, "foto.jpg")),
		//		//	returnFaceId: true,
		//		//	returnFaceLandmarks: false,
		//		//	returnFaceAttributes: requestedFaceAttribs,
		//		//	// We specify detection model 1 because we are retrieving attributes.
		//		//	detectionModel: DetectionModel.Detection01,
		//		//	recognitionModel: recognitionModel
		//		//	);

		//		// Detect faces with all attributes from image url.
		//		detectedFaces = await client.Face.DetectWithUrlAsync
		//			(
		//			url: $"{url}{imageFileName}",
		//			returnFaceId: true,
		//			returnFaceLandmarks: false,
		//			returnFaceAttributes: _requestedFaceAttribs,
		//			// We specify detection model 1 because we are retrieving attributes.
		//			detectionModel: DetectionModel.Detection01,
		//			recognitionModel: recognitionModel
		//			);

		//		Console.WriteLine($"{detectedFaces.Count} face(s) detected from image: {imageFileName}.");

		//		foreach (var detectedFace in detectedFaces)
		//			{
		//			ExtractFaceInfo(detectedFace, imageFileName);
		//			}
		//		}
		//	}
