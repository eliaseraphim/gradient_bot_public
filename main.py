# author: elia deppe
# date: 05/05/21

# acronyms
# rgb | red green blue

# imports - namespace
import math
from random import randint, randrange, choice
from PIL import Image


# import - module
import tweepy

# 1024 ^ 2 == 1048576
# 1048576 + 1048576 == 2097152
SIZE = 1024  # image size - 1024 pixels x 1024 pixels
HYPOTENUSE = math.ceil(pow(2097152, .5))  # size of the hypotenuse of the image
ORIGINS = ('left', 'right', 'top', 'bottom', 'top_left', 'top_right', 'bottom_left', 'bottom_right')


# function
# generate_switch_points
# 	parameters
# 		origin        | string          | the origin of a linear gradient. this is one of the elements from ORIGINS
# 		num_colors    | integer         | the number of colors to generate
#
# 	return value
# 		switch_points | List [Integers] | the distances on the image at which to switch colors for interpolation
#
# description: generates the points at which you would switch interpolating one color to another on the image.
# 	these are distances based on the function:
# 		distance = floor(x * (length / num_colors - 1))
# 			where:
# 				i = current colors index in the list
# 				length = {SIZE when the origin does not contain a '_' in the string, otherwise HYPOTENUSE}
# 				num_colors = the number of colors to generate
#
# 		this means that the initial switch point is always 0, and the last will always be length
#
# 	these distances are appended to the list switch_points, which is then returned
def generate_switch_points(origin, num_colors):
	switch_points = []

	if origin.count('_') == 0:
		for i in range(num_colors):
			switch_points.append(int(i * (SIZE / (num_colors - 1))))

	else:
		for i in range(num_colors):
			switch_points.append(int(i * (HYPOTENUSE / (num_colors - 1))))

	return switch_points


# function
# generate_colors
# 	parameters
# 		num_colors | Integer | number of colors to generate
#
# 	return value
# 		colors     | Tuple   | a tuple of rgb codes in list form, meant to be the colors for the gradient
#
# description: generate a tuple of colors to be used for linear interpolation functions. the rgb codes generated
# 	are lists of red, green, and blue values in decimal form
def generate_colors(num_colors):
	colors = [[] for i in range(num_colors)]

	for rgb_code in colors:
		for i in range(3):
			rgb_code.append(randint(0, 255))

	return tuple(colors)


# function
# generate_origins
# 	parameters
# 		none
#
# 	return value
# 		origins | Tuple (Lists [Integers]) | a set of three coordinates, designating the origins of the red, green,
# 												and blue channels
#
# description: generates the origins of the red, green, and blue channels. these origins are positions on the
#
def generate_origins(num_origins):
	origins = []

	for i in range(num_origins):
		origins.append([randrange(0, SIZE), randrange(0, SIZE)])

	return tuple(origins)


def distance(x1, y1, x2, y2):
	return int(pow((x1 - x2) ** 2 + (y1 - y2) ** 2, .5))


# function
# find_divisors
# 	parameters
# 		origins  | Tuple (Lists [Integers]) | a set of three coordinates, designating the origins of the red, green,
# 												and blue channels
# 	return value
# 		divisors | List [Integers]          | generates a maximum distance from the origin to the farthest corner
# 												of the shape, for every origin
#
# description: this functions finds the maximum distance between a a point of origin within the 1024 x 1024 pixel grid
# 	the furthest corner. the furthest corner of the grid is in the opposite (horizontally and vertically) quadrant
# 	of the square grid.
def find_divisors(origins):
	divisors = []

	for origin in origins:
		# top left quadrant
		# 	furthest point is bottom right corner, or (1023, 1023)
		if origin[0] < SIZE // 2 and origin[1] < SIZE // 2:
			max_distance = distance(SIZE - 1, SIZE - 1, origin[0], origin[1])

		# top right quadrant
		# 	furthest point is bottom left, or (0, 1023)
		elif origin[0] > SIZE // 2 > origin[1]:
			max_distance = distance(0, SIZE - 1, origin[0], origin[1])

		# bottom left quadrant
		# 	furthest point is top right corner, or (1023, 0)
		elif origin[0] < SIZE // 2 < origin[1]:
			max_distance = distance(SIZE - 1, 0, origin[0], origin[1])

		# bottom right quadrant
		# 	furthest point is top left corner, or (0, 0)
		else:
			max_distance = distance(0, 0, origin[0], origin[1])

		divisors.append(max_distance)

	return divisors


def lerp(channel1, channel2, current_distance, max_distance):
	return int(channel1 + (channel2 - channel1) * (current_distance / max_distance))


# function
# linear_gradient
# 	parameters
# 		img | Image | the image object used for the gradient
#
# 	return value
# 		img | Image | the image object used for the gradient
#
# description: one of the choices for generating a gradient image. linear gradient generates a linear gradient between
# 	[2, 4] colors. the linear gradient can originate from any of the sides or corners.
#
# Note: Could implement this to adjust based on angle, eliminating the need to rotate the image. Not sure on the math
# 	and this accomplishes it without much need for math.
def linear_gradient(img):
	origin = choice(ORIGINS)
	colors = generate_colors(randint(2, 4))
	switch_points = generate_switch_points(origin, len(colors))

	if origin.count('_') == 0:
		horizontal_gradient(img, colors, switch_points)

		if origin == 'top':
			img = img.rotate(angle=90)
		elif origin == 'right':
			img = img.rotate(angle=180)
		elif origin == 'bottom':
			img = img.rotate(angle=270)
	else:
		diagonal_gradient(img, colors, switch_points)

		if origin == 'top_right':
			img = img.rotate(angle=90)
		elif origin == 'bottom_right':
			img = img.rotate(angle=180)
		elif origin == 'bottom_left':
			img = img.rotate(angle=180)

	return img


# function
# horizontal_gradient
# 	parameters
# 		img           | Image                    | the image object used for the gradient
# 		colors        | Tuple [Lists [Integers]] | the rgb codes for the colors in the gradient
# 		switch_points | List [Integers]          | the distances at which colors switch
#
# description: generates a horizontal gradient on the img object from left to right using the colors within the
# 	tuple colors.
def horizontal_gradient(img, colors, switch_points):
	position = 0

	for x in range(SIZE):
		rgb = []
		for i in range(3):
			rgb.append(
				lerp(colors[position][i], colors[position + 1][i], x - switch_points[position], switch_points[1])
			)

		for y in range(SIZE):
			img.putpixel((x, y), tuple(rgb))

			if x == switch_points[position + 1]:
				position += 1


# function
# diagonal gradient
# 	parameters
# 		img           | Image                    | the image object used for the gradient
# 		colors        | Tuple [Lists [Integers]] | the rgb codes for the colors in the gradient
# 		switch_points | List [Integers]          | the distances at which colors switch
#
# description: generates a diagonal gradient on the img object from left to right using the colors within the
# 	tuple colors.
def diagonal_gradient(img, colors, switch_points):
	for x in range(SIZE):
		for y in range(SIZE):
			rgb = []
			net_direction = -x + y
			origin = (-.5 * net_direction, .5 * net_direction)
			d = distance(origin[0], origin[1], x, y)

			position = 0
			for i in range(len(switch_points)):
				if d > switch_points[i]:
					position = i

			for i in range(3):
				rgb.append(
					lerp(colors[position][i], colors[position + 1][i], d - switch_points[position], switch_points[1])
				)

			img.putpixel((x, y), tuple(rgb))


# function
# radial_gradient
# 	parameters
# 		img | Image | the image object used for the gradient
#
# 	return value
# 		img | Image | the image object used for the gradient
#
# description: creates a radial gradient of two colors originating from a random point on the canvas within the range
# 	[0, 1024). img is returned out of necessity due to linear gradient requiring to return the image
def radial_gradient(img):
	origin = (randint(0, SIZE), randint(0, SIZE))
	colors = generate_colors(2)

	for x in range(SIZE):
		for y in range(SIZE):
			rgb = []
			d = distance(origin[0], origin[1], x, y)

			for i in range(3):
				rgb.append(lerp(colors[0][i], colors[1][i], d, HYPOTENUSE))

			img.putpixel((x, y), tuple(rgb))

	return img


def radial_channel_strength(img):
	origins = generate_origins(3)
	functions = {
		1: radial_channel_strength_size,
		2: radial_channel_strength_hypotenuse,
		3: radial_channel_strength_measured
	}

	img = functions.get(randint(1, len(functions)))(img, origins)

	return img


def radial_channel_strength_size(img, origins):
	for x in range(SIZE):
		for y in range(SIZE):
			rgb = []
			for i in range(3):
				d = distance(origins[i][0], origins[i][1], x, y)
				rgb.append(lerp(255, 0, min(SIZE, d), SIZE))

			img.putpixel((x, y), tuple(rgb))

	return img


def radial_channel_strength_hypotenuse(img, origins):
	for x in range(SIZE):
		for y in range(SIZE):
			rgb = []
			for i in range(3):
				d = distance(origins[i][0], origins[i][1], x, y)
				rgb.append(lerp(255, 0, d, HYPOTENUSE))

			img.putpixel((x, y), tuple(rgb))

	return img


def radial_channel_strength_measured(img, origins):
	divisors = find_divisors(origins)

	for x in range(SIZE):
		for y in range(SIZE):
			rgb = []
			for i in range(3):
				d = distance(origins[i][0], origins[i][1], x, y)
				rgb.append(lerp(255, 0, d, divisors[i]))

			img.putpixel((x, y), tuple(rgb))

	return img


# function
# generate_image
def generate_image(img):
	functions = {
		1: linear_gradient,
		2: radial_gradient,
		3: radial_channel_strength,
	}

	img = functions.get(randint(1, len(functions)))(img)   # generate function and call it, passing along original img object

	return img


# function
# main
def main():
	# create our authentication token using our credentials
	# --> then bind the twitter bot's access token to our credentials
	auth = tweepy.OAuthHandler('access_key', 'access_key_secret')
	auth.set_access_token('access_token', 'access_token_secret')

	# establish the handshake between our program and the twitter API using our authentication token
	api = tweepy.API(auth)

	# Creates a new image of size 1024 x 1024 pixels, and coloring scheme: RGBA
	img = Image.new('RGBA', (1024, 1024))
	img = generate_image(img)

	# saves the image to our directory
	img.save('./gradient.png')

	# updates our twitter with the gradient image
	api.update_with_media('./gradient.png')

	img.close()


if __name__ == '__main__':
	main()
