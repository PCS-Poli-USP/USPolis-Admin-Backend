from flasgger import Schema, fields

class ArraySumField(fields.Field):
  """
  fields to sum array values
  """
  def _deserialize(self, value, _, __, **___):
    return sum(value)


class PreferencesSchema(Schema):
  building = fields.Str(required=True)
  air_conditioning = fields.Bool()
  projector = fields.Bool()
  accessibility = fields.Bool()


class ClassSchema(Schema):
  class_code = fields.Str(data_key="cod_turma")
  subject_code = fields.Str(data_key="cod_disciplina")
  subject_name = fields.Str(data_key="nome_disciplina")
  professors = fields.List(fields.Str(), data_key="prof")
  start_period = fields.Str(data_key="inicio")
  end_period = fields.Str(data_key="fim")
  start_time=fields.List(fields.Str(), data_key="hora_inicio")
  end_time=fields.List(fields.Str(), data_key="hora_fim")
  week_days=fields.List(fields.Str(), data_key="dia_semana")
  class_type = fields.Str(data_key="tipo")
  vacancies = ArraySumField(data_key="vagas")
  subscribers = ArraySumField(data_key="inscritos")
  pendings = ArraySumField(data_key="pendentes")


class HasToBeAllocatedClassesSchema(Schema):
  class_code = fields.Str()
  subject_code = fields.Str()
  has_to_be_allocated = fields.Bool()
