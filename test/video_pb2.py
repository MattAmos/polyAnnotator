# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: video.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='video.proto',
  package='PolyAnnotator',
  syntax='proto2',
  serialized_pb=_b('\n\x0bvideo.proto\x12\rPolyAnnotator\"\xa9\x02\n\x05Video\x12\x0c\n\x04path\x18\x01 \x02(\t\x12\r\n\x05width\x18\x02 \x01(\x05\x12\x0e\n\x06height\x18\x03 \x01(\x05\x12)\n\x05\x66rame\x18\x04 \x03(\x0b\x32\x1a.PolyAnnotator.Video.Frame\x1a\xc7\x01\n\x05\x46rame\x12\x0f\n\x07\x66rameNo\x18\x01 \x02(\x05\x12\x39\n\nannotation\x18\x02 \x03(\x0b\x32%.PolyAnnotator.Video.Frame.Annotation\x1ar\n\nAnnotation\x12\r\n\x05label\x18\x01 \x02(\t\x12\x36\n\x01p\x18\x02 \x03(\x0b\x32+.PolyAnnotator.Video.Frame.Annotation.Point\x1a\x1d\n\x05Point\x12\t\n\x01x\x18\x01 \x02(\x05\x12\t\n\x01y\x18\x02 \x02(\x05')
)




_VIDEO_FRAME_ANNOTATION_POINT = _descriptor.Descriptor(
  name='Point',
  full_name='PolyAnnotator.Video.Frame.Annotation.Point',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='x', full_name='PolyAnnotator.Video.Frame.Annotation.Point.x', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='y', full_name='PolyAnnotator.Video.Frame.Annotation.Point.y', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=299,
  serialized_end=328,
)

_VIDEO_FRAME_ANNOTATION = _descriptor.Descriptor(
  name='Annotation',
  full_name='PolyAnnotator.Video.Frame.Annotation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='label', full_name='PolyAnnotator.Video.Frame.Annotation.label', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='p', full_name='PolyAnnotator.Video.Frame.Annotation.p', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_VIDEO_FRAME_ANNOTATION_POINT, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=214,
  serialized_end=328,
)

_VIDEO_FRAME = _descriptor.Descriptor(
  name='Frame',
  full_name='PolyAnnotator.Video.Frame',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frameNo', full_name='PolyAnnotator.Video.Frame.frameNo', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='annotation', full_name='PolyAnnotator.Video.Frame.annotation', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_VIDEO_FRAME_ANNOTATION, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=129,
  serialized_end=328,
)

_VIDEO = _descriptor.Descriptor(
  name='Video',
  full_name='PolyAnnotator.Video',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='PolyAnnotator.Video.path', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='width', full_name='PolyAnnotator.Video.width', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='height', full_name='PolyAnnotator.Video.height', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='frame', full_name='PolyAnnotator.Video.frame', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_VIDEO_FRAME, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=31,
  serialized_end=328,
)

_VIDEO_FRAME_ANNOTATION_POINT.containing_type = _VIDEO_FRAME_ANNOTATION
_VIDEO_FRAME_ANNOTATION.fields_by_name['p'].message_type = _VIDEO_FRAME_ANNOTATION_POINT
_VIDEO_FRAME_ANNOTATION.containing_type = _VIDEO_FRAME
_VIDEO_FRAME.fields_by_name['annotation'].message_type = _VIDEO_FRAME_ANNOTATION
_VIDEO_FRAME.containing_type = _VIDEO
_VIDEO.fields_by_name['frame'].message_type = _VIDEO_FRAME
DESCRIPTOR.message_types_by_name['Video'] = _VIDEO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Video = _reflection.GeneratedProtocolMessageType('Video', (_message.Message,), dict(

  Frame = _reflection.GeneratedProtocolMessageType('Frame', (_message.Message,), dict(

    Annotation = _reflection.GeneratedProtocolMessageType('Annotation', (_message.Message,), dict(

      Point = _reflection.GeneratedProtocolMessageType('Point', (_message.Message,), dict(
        DESCRIPTOR = _VIDEO_FRAME_ANNOTATION_POINT,
        __module__ = 'video_pb2'
        # @@protoc_insertion_point(class_scope:PolyAnnotator.Video.Frame.Annotation.Point)
        ))
      ,
      DESCRIPTOR = _VIDEO_FRAME_ANNOTATION,
      __module__ = 'video_pb2'
      # @@protoc_insertion_point(class_scope:PolyAnnotator.Video.Frame.Annotation)
      ))
    ,
    DESCRIPTOR = _VIDEO_FRAME,
    __module__ = 'video_pb2'
    # @@protoc_insertion_point(class_scope:PolyAnnotator.Video.Frame)
    ))
  ,
  DESCRIPTOR = _VIDEO,
  __module__ = 'video_pb2'
  # @@protoc_insertion_point(class_scope:PolyAnnotator.Video)
  ))
_sym_db.RegisterMessage(Video)
_sym_db.RegisterMessage(Video.Frame)
_sym_db.RegisterMessage(Video.Frame.Annotation)
_sym_db.RegisterMessage(Video.Frame.Annotation.Point)


# @@protoc_insertion_point(module_scope)