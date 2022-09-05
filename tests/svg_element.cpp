#include <cassert>
#include <limits>
#include <stdexcept>

#include <fmt/format.h>

#include "svg_element.h"
#include <cgraph/unreachable.h>

SVG::SVGElement::SVGElement(SVGElementType type) : type(type) {}

static double px_to_pt(double px) {
  // a `pt` is 0.75 `px`. See e.g.
  // https://oreillymedia.github.io/Using_SVG/guide/units.html
  return px * 3 / 4;
}

bool SVG::SVGElement::is_shape_element() const {
  switch (type) {
  case SVG::SVGElementType::Circle:
  case SVG::SVGElementType::Ellipse:
  case SVG::SVGElementType::Line:
  case SVG::SVGElementType::Path:
  case SVG::SVGElementType::Polygon:
  case SVG::SVGElementType::Polyline:
  case SVG::SVGElementType::Rect:
    return true;
  default:
    return false;
  }
}

static std::string xml_encode(const std::string &text) {
  std::string out;
  for (const char &ch : text) {
    switch (ch) {
    case '>':
      out += "&gt;";
      break;
    case '<':
      out += "&lt;";
      break;
    case '-':
      out += "&#45;";
      break;
    case '&':
      out += "&amp;";
      break;
    default:
      out += ch;
    }
  }
  return out;
}

// convert a valid color specification to the flavor that Graphviz uses
static std::string to_graphviz_color(const std::string &color) {
  if (color == "rgb(0,0,0)") {
    return "black";
  } else if (color == "rgb(255,255,255)") {
    return "white";
  } else if (color.starts_with("rgb")) {
    const auto comma1 = color.find_first_of(",");
    const auto r = std::stoi(color.substr(4, comma1 - 1));
    const auto comma2 = color.find_first_of(",", comma1 + 1);
    const auto g = std::stoi(color.substr(comma1 + 1, comma2 - 1));
    const auto close_par = color.find_first_of(")", comma2 + 1);
    const auto b = std::stoi(color.substr(comma2 + 1, close_par - 1));
    return fmt::format("#{:02x}{:02x}{:02x}", r, g, b);
  } else {
    return color;
  }
}

SVG::SVGRect SVG::SVGElement::bbox(bool throw_if_bbox_not_defined) {
  if (!m_bbox.has_value()) {
    // negative width and height bbox that will be imediately replaced by the
    // first bbox found
    m_bbox = {.x = std::numeric_limits<double>::max() / 2,
              .y = std::numeric_limits<double>::max() / 2,
              .width = std::numeric_limits<double>::lowest(),
              .height = std::numeric_limits<double>::lowest()};
    switch (type) {
    case SVG::SVGElementType::Group:
      // SVG group bounding box is detemined solely by its children
      break;
    case SVG::SVGElementType::Ellipse: {
      m_bbox = {
          .x = attributes.cx - attributes.rx,
          .y = attributes.cy - attributes.ry,
          .width = attributes.rx * 2,
          .height = attributes.ry * 2,
      };
      break;
    }
    case SVG::SVGElementType::Polygon:
    case SVG::SVGElementType::Polyline: {
      for (const auto &point : attributes.points) {
        m_bbox->extend(point);
      }
      break;
    }
    case SVG::SVGElementType::Path: {
      if (path_points.empty()) {
        throw std::runtime_error{"No points for 'path' element"};
      }
      for (const auto &point : path_points) {
        m_bbox->extend(point);
      }
      break;
    }
    case SVG::SVGElementType::Rect: {
      m_bbox = {
          .x = attributes.x,
          .y = attributes.y,
          .width = attributes.width,
          .height = attributes.height,
      };
      break;
    }
    case SVG::SVGElementType::Text: {
      m_bbox = text_bbox();
      break;
    }
    case SVG::SVGElementType::Title:
      // title has no size
      if (throw_if_bbox_not_defined) {
        throw std::runtime_error{"A 'title' element has no bounding box"};
      }
      break;
    default:
      throw std::runtime_error{
          fmt::format("Unhandled svg element type {}", tag(type))};
    }

    const auto throw_if_child_bbox_is_not_defined = false;
    for (auto &child : children) {
      const auto child_bbox = child.bbox(throw_if_child_bbox_is_not_defined);
      m_bbox->extend(child_bbox);
    }
  }

  return *m_bbox;
}

SVG::SVGRect SVG::SVGElement::text_bbox() const {
  assert(type == SVG::SVGElementType::Text && "Not a 'text' element");

  if (attributes.font_family != "Courier,monospace") {
    throw std::runtime_error(
        fmt::format("Cannot calculate bounding box for font \"{}\"",
                    attributes.font_family));
  }

  // Epirically determined font metrics for the Courier font
  const auto courier_width_per_pt = 0.6;
  const auto courier_height_per_pt = 1.2;
  const auto descent_per_pt = 1.0 / 3.0;
  const auto font_width = attributes.font_size * courier_width_per_pt;
  const auto font_height = attributes.font_size * courier_height_per_pt;
  const auto descent = attributes.font_size * descent_per_pt;

  const SVG::SVGRect bbox = {
      .x = attributes.x - font_width * text.size() / 2,
      .y = attributes.y - font_height + descent,
      .width = font_width * text.size(),
      .height = font_height,
  };
  return bbox;
}

void SVG::SVGElement::append_attribute(std::string &output,
                                       const std::string &attribute) const {
  if (attribute.empty()) {
    return;
  }
  if (!output.empty()) {
    output += " ";
  }
  output += attribute;
}

std::string SVG::SVGElement::fill_attribute_to_string() const {
  if (attributes.fill.empty()) {
    return "";
  }

  return fmt::format(R"(fill="{}")", to_graphviz_color(attributes.fill));
}

std::string SVG::SVGElement::id_attribute_to_string() const {
  if (attributes.id.empty()) {
    return "";
  }

  return fmt::format(R"(id="{}")", attributes.id);
}

std::string SVG::SVGElement::points_attribute_to_string() const {
  std::string points_attribute_str = R"|(points=")|";
  const char *separator = "";
  for (const auto &point : attributes.points) {
    points_attribute_str += separator + fmt::format("{},{}", point.x, point.y);
    separator = " ";
  }
  points_attribute_str += '"';

  return points_attribute_str;
}

std::string SVG::SVGElement::stroke_attribute_to_string() const {
  if (attributes.stroke.empty()) {
    return "";
  }

  return fmt::format(R"(stroke="{}")",
                     stroke_to_graphviz_color(attributes.stroke));
}

std::string SVG::SVGElement::stroke_opacity_attribute_to_string() const {
  if (attributes.stroke_opacity == 1) {
    // Graphviz doesn't set `stroke-opacity` to 1 since that's the default
    return "";
  }

  if (attributes.stroke_opacity == 0) {
    // Graphviz doesn't set `stroke-opacity` to 0 since in that case it sets
    // `stroke` to "none" instead
    return "";
  }

  return fmt::format(R"(stroke-opacity="{}")", attributes.stroke_opacity);
}

std::string SVG::SVGElement::stroke_width_attribute_to_string() const {
  if (attributes.stroke_width == 1) {
    // Graphviz doesn't set `stroke-width` to 1 since that's the default
    return "";
  }

  return fmt::format(R"(stroke-width="{}")", attributes.stroke_width);
}

std::string SVG::SVGElement::to_string(std::size_t indent_size = 2) const {
  std::string output;
  output += R"(<?xml version="1.0" encoding="UTF-8" standalone="no"?>)"
            "\n";
  output += R"(<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN")"
            "\n";
  output += R"( "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">)"
            "\n";
  output += fmt::format("<!-- Generated by graphviz version {} "
                        "({})\n -->\n",
                        graphviz_version, graphviz_build_date);
  to_string_impl(output, indent_size, 0);
  return output;
}

void SVG::SVGElement::to_string_impl(std::string &output,
                                     std::size_t indent_size,
                                     std::size_t current_indent) const {
  const auto indent_str = std::string(current_indent, ' ');
  output += indent_str;

  if (type == SVG::SVGElementType::Svg) {
    const auto comment = fmt::format("Title: {} Pages: 1", graphviz_id);
    output += fmt::format("<!-- {} -->\n", xml_encode(comment));
  }
  if (type == SVG::SVGElementType::Group &&
      (attributes.class_ == "node" || attributes.class_ == "edge")) {
    const auto comment = graphviz_id;
    output += fmt::format("<!-- {} -->\n", xml_encode(comment));
  }

  output += "<";
  output += tag(type);

  std::string attributes_str{};
  append_attribute(attributes_str, id_attribute_to_string());
  switch (type) {
  case SVG::SVGElementType::Ellipse:
    append_attribute(attributes_str, fill_attribute_to_string());
    append_attribute(attributes_str, stroke_attribute_to_string());
    append_attribute(attributes_str, stroke_width_attribute_to_string());
    append_attribute(attributes_str, stroke_opacity_attribute_to_string());
    attributes_str +=
        fmt::format(R"( cx="{}" cy="{}" rx="{}" ry="{}")", attributes.cx,
                    attributes.cy, attributes.rx, attributes.ry);
    break;
  case SVG::SVGElementType::Group:
    attributes_str += fmt::format(R"( class="{}")", attributes.class_);
    if (attributes.transform.has_value()) {
      const auto transform = attributes.transform;
      attributes_str += fmt::format(
          R"|( transform="scale({} {}) rotate({}) translate({} {})")|",
          transform->a, transform->d, transform->c, transform->e, transform->f);
    }
    break;
  case SVG::SVGElementType::Path: {
    append_attribute(attributes_str, fill_attribute_to_string());
    append_attribute(attributes_str, stroke_attribute_to_string());
    append_attribute(attributes_str, stroke_width_attribute_to_string());
    append_attribute(attributes_str, stroke_opacity_attribute_to_string());
    attributes_str += R"|( d=")|";
    auto command = 'M';
    for (const auto &point : path_points) {
      attributes_str += fmt::format("{}{},{}", command, point.x, point.y);
      switch (command) {
      case 'M':
        command = 'C';
        break;
      case 'C':
        command = ' ';
        break;
      case ' ':
        break;
      default:
        UNREACHABLE();
      }
    }
    attributes_str += '"';
    break;
  }
  case SVG::SVGElementType::Polygon:
    append_attribute(attributes_str, fill_attribute_to_string());
    append_attribute(attributes_str, stroke_attribute_to_string());
    append_attribute(attributes_str, stroke_width_attribute_to_string());
    append_attribute(attributes_str, stroke_opacity_attribute_to_string());
    append_attribute(attributes_str, points_attribute_to_string());
    break;
  case SVG::SVGElementType::Polyline:
    append_attribute(attributes_str, fill_attribute_to_string());
    append_attribute(attributes_str, stroke_attribute_to_string());
    append_attribute(attributes_str, stroke_width_attribute_to_string());
    append_attribute(attributes_str, stroke_opacity_attribute_to_string());
    append_attribute(attributes_str, points_attribute_to_string());
    break;
  case SVG::SVGElementType::Svg:
    attributes_str += fmt::format(
        R"(width="{}pt" height="{}pt")"
        "\n"
        R"( viewBox="{:.2f} {:.2f} {:.2f} {:.2f}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink")",
        std::lround(px_to_pt(attributes.width)),
        std::lround(px_to_pt(attributes.height)), attributes.viewBox.x,
        attributes.viewBox.y, attributes.viewBox.width,
        attributes.viewBox.height);
    break;
  case SVG::SVGElementType::Text:
    attributes_str += fmt::format(
        R"(text-anchor="{}" x="{}" y="{}" font-family="{}" font-size="{:.2f}")",
        attributes.text_anchor, attributes.x, attributes.y,
        attributes.font_family, attributes.font_size);
    break;
  case SVG::SVGElementType::Title:
    // Graphviz doesn't generate attributes on 'title' elements
    break;
  default:
    throw std::runtime_error{fmt::format(
        "Attributes on '{}' elements are not yet implemented", tag(type))};
  }
  if (!attributes_str.empty()) {
    output += " ";
  }
  output += attributes_str;

  if (children.empty() && text.empty()) {
    output += "/>\n";
  } else {
    output += ">";
    if (!text.empty()) {
      output += xml_encode(text);
    }
    if (!children.empty()) {
      output += "\n";
      for (const auto &child : children) {
        child.to_string_impl(output, indent_size, current_indent + indent_size);
      }
      output += indent_str;
    }
    output += "</";
    output += tag(type);
    output += ">\n";
  }
}

std::string
SVG::SVGElement::stroke_to_graphviz_color(const std::string &color) const {
  return to_graphviz_color(color);
}

void SVG::SVGRect::extend(const SVGPoint &point) {
  const auto xmin = std::min(x, point.x);
  const auto ymin = std::min(y, point.y);
  const auto xmax = std::max(x + width, point.x);
  const auto ymax = std::max(y + height, point.y);

  x = xmin;
  y = ymin;
  width = xmax - xmin;
  height = ymax - ymin;
}

SVG::SVGPoint SVG::SVGRect::center() const {
  return {x + width / 2, y + height / 2};
}

void SVG::SVGRect::extend(const SVG::SVGRect &other) {
  const auto xmin = std::min(x, other.x);
  const auto ymin = std::min(y, other.y);
  const auto xmax = std::max(x + width, other.x + other.width);
  const auto ymax = std::max(y + height, other.y + other.height);

  x = xmin;
  y = ymin;
  width = xmax - xmin;
  height = ymax - ymin;
}

std::string_view SVG::tag(SVGElementType type) {
  switch (type) {
  case SVG::SVGElementType::Circle:
    return "circle";
  case SVG::SVGElementType::Ellipse:
    return "ellipse";
  case SVG::SVGElementType::Group:
    return "g";
  case SVG::SVGElementType::Line:
    return "line";
  case SVG::SVGElementType::Path:
    return "path";
  case SVG::SVGElementType::Polygon:
    return "polygon";
  case SVG::SVGElementType::Polyline:
    return "polyline";
  case SVG::SVGElementType::Rect:
    return "rect";
  case SVG::SVGElementType::Svg:
    return "svg";
  case SVG::SVGElementType::Text:
    return "text";
  case SVG::SVGElementType::Title:
    return "title";
  }
  UNREACHABLE();
}

bool SVG::SVGPoint::is_higher_than(const SVGPoint &other) const {
  // SVG uses inverted y axis, so smaller is higher
  return y < other.y;
}

bool SVG::SVGPoint::is_lower_than(const SVGPoint &other) const {
  // SVG uses inverted y axis, so larger is lower
  return y > other.y;
}

bool SVG::SVGPoint::is_more_left_than(const SVGPoint &other) const {
  return x < other.x;
}

bool SVG::SVGPoint::is_more_right_than(const SVGPoint &other) const {
  return x > other.x;
}
